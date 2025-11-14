import prisma from '../../config/prismaClient.js'

interface Researcher{
  id: string,
  name: string,
  tags: string[] // O frontend precisa disso
}

async function getTagByName(tagName:string){
  const result = await prisma.researcher_tags.findFirst({
    where:{
      name: tagName
    }
  })
  return result
}

export async function searchResearchersByTag(tagName: string): Promise<Researcher[]>{
    const tag = await getTagByName(tagName);
    if (tag == null) {
      console.warn(`[API] Tag não encontrada: ${tagName}`);
      return []
    }

    // --- PASSO 1: Buscar os pesquisadores (Sua lógica original) ---
    // Encontra todos os pesquisadores que têm a tag pai (ex: "Química")
    const initialResults = await prisma.researcher_tags_on_researchers.findMany({
      where: {
        tag_id: tag.id
      },
      select:{
        researcher: {
          select:{
            id: true,
            name: true
          }
        }
      },
    })

    if (initialResults.length === 0) {
      console.warn(`[API] Nenhum pesquisador encontrado para a tag: ${tagName}`);
      return [];
    }

    // Extrai os IDs dos pesquisadores encontrados
    const researcherIds = initialResults.map(r => r.researcher.id);
    // researcherIds agora é algo como: ['id-do-hugo', 'id-da-tatiane', ...]

    // --- PASSO 2: Buscar TODAS as tags para ESSES pesquisadores ---
    // Agora, buscamos todas as relações de tags para os pesquisadores que encontramos
    const allTagLinks = await prisma.researcher_tags_on_researchers.findMany({
      where: {
        researcher_id: { in: researcherIds } // "onde o ID do pesquisador esteja NESSA lista"
      },
      select: {
        researcher_id: true,
        tag: { // E para cada relação, pegue o nome da tag
          select: {
            name: true
          }
        }
      }
    });

    // --- PASSO 3: Mapear as tags para cada pesquisador ---
    // Criamos um "dicionário" (Map) para agrupar as tags por ID
    const tagsByResearcher = new Map<string, string[]>();
    for (const link of allTagLinks) {
      if (!tagsByResearcher.has(link.researcher_id)) {
        tagsByResearcher.set(link.researcher_id, []);
      }
      tagsByResearcher.get(link.researcher_id)!.push(link.tag.name);
    }
    
    return initialResults.map(r => {
      const researcher = r.researcher;
      const tags = tagsByResearcher.get(researcher.id) || []; // Pega as tags do Map

      return {
        id: researcher.id,
        name: researcher.name,
        tags: tags 
      };
    });
}