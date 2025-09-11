import prisma from '../../config/prismaClient.js'

interface Researcher{
  id: string,
  name: string
}

export async function searchResearchersByTag(tag: string): Promise<Researcher[]>{
    const results = await prisma.researcher_tags_on_researchers.findMany({
      where: {
        tag_id: tag
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
    return results.map(r => r.researcher);
}