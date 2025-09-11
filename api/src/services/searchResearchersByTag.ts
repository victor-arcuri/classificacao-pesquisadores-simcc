import prisma from '../../config/prismaClient.js'

interface Researcher{
  id: string,
  name: string
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
    if (tag == null) return []
    const results = await prisma.researcher_tags_on_researchers.findMany({
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
    return results.map(r => r.researcher);
}