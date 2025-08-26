import prisma from '../../config/prismaClient.js'
import { MatchingTag } from '../types/search.js';

function normalizeQuery(query: string) {
  return query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
}

export async function searchTag(query: string, minTsRank: number = 0.01, minTrgmScore: number = 0.15): Promise<MatchingTag[]>{
    const normalizedQuery = normalizeQuery(query);
    const tsQueryString = normalizedQuery.split(/\s+/).join(' & ');
    console.log(tsQueryString)

    const results = await prisma.$queryRawUnsafe<MatchingTag[]>(`
    SELECT
      id,
      name,
      ts_rank("search_vector", to_tsquery('portuguese_unaccent', $1)) AS ts_score,
      similarity(LOWER(unaccent("name")), LOWER(unaccent($2))) AS trgm_score
    FROM
      "public"."researcher_tags"
    WHERE
      ts_rank("search_vector", to_tsquery('portuguese_unaccent', $1)) > $3 OR
      similarity(LOWER(unaccent("name")), LOWER(unaccent($2))) > $4
    ORDER BY
      ts_rank("search_vector", to_tsquery('portuguese_unaccent', $1)) * 0.7 +
      similarity(LOWER(unaccent("name")), LOWER(unaccent($2))) * 0.4
    DESC
    LIMIT 10;
    `,
    tsQueryString,
    normalizedQuery,
    minTsRank,
    minTrgmScore
  );
      return results;
}