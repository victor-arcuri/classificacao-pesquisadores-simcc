import prisma from '../../config/prismaClient.js'
import { MatchingTag } from '../types/search.js';

function normalizeQuery(query: string) {
  return query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
}

export async function searchTag(query: string, minTsRank: number = 0.01, minTrgmScore: number = 0.25): Promise<MatchingTag[]>{
    const normalizedQuery = normalizeQuery(query);
    const tsQueryString = normalizedQuery.split(/\s+/).join(' & ');
    console.log(tsQueryString)

    const results = await prisma.$queryRawUnsafe<MatchingTag[]>(`
    SELECT
      public.researcher_tags.id AS id,
      public.researcher_tags.name AS name,
      ts_rank(public.researcher_tags.search_vector, to_tsquery('portuguese_unaccent', $1)) AS ts_score,
      similarity(LOWER(unaccent(public.researcher_tags.name)), LOWER(unaccent($2))) AS trgm_score,
      public.tags_hierarchy.parent_tag_id AS "idDadTag",
      CASE WHEN public.tags_hierarchy.parent_tag_id IS NOT NULL THEN TRUE ELSE FALSE END AS "isDadTag",
      ARRAY_AGG(DISTINCT child.name)
        FILTER (WHERE child.name IS NOT NULL) AS "childTags"
    FROM
      public.researcher_tags
    LEFT JOIN
      public.tags_hierarchy
        ON public.researcher_tags.id = public.tags_hierarchy.parent_tag_id
    LEFT JOIN
      public.researcher_tags AS child
        ON child.id = public.tags_hierarchy.tag_id
    WHERE
      ts_rank(public.researcher_tags.search_vector, to_tsquery('portuguese_unaccent', $1)) > $3
      OR similarity(
          LOWER(unaccent(public.researcher_tags.name)),
          LOWER(unaccent($2))
        ) > $4
    GROUP BY
      public.researcher_tags.id,
      public.researcher_tags.name,
      public.tags_hierarchy.parent_tag_id,
      public.researcher_tags.search_vector
    ORDER BY
      -- Passo 1: Prioriza resultados que tiveram qualquer pontuação semântica
      CASE WHEN ts_rank(public.researcher_tags.search_vector, to_tsquery('portuguese_unaccent', $1)) > 0 THEN 1 ELSE 0 END DESC,
      
      -- Passo 2: Para os resultados que passaram no passo 1, ordena pelo score combinado
      (
        ts_rank(public.researcher_tags.search_vector, to_tsquery('portuguese_unaccent', $1)) * 0.9 +
        similarity(
          LOWER(unaccent(public.researcher_tags.name)),
          LOWER(unaccent($2))
        ) * 0.1
      ) DESC
    LIMIT 10;
  `,
    tsQueryString,
    normalizedQuery,
    minTsRank,
    minTrgmScore
  );
      return results;
}