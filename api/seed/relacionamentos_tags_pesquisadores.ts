import { Prisma } from '@prisma/client'
import prisma from '../config/prismaClient.js'
 
async function retomarTags () {
    const tags = await prisma.researcher_tags.findMany()
    return tags;
} 

async function retomarPesquisadorAleatorio(){
    const researcher = await prisma.public_researcher.findRandom({
        select:{   
            name: true,
            id: true
        }
    });
    return researcher;
}

async function atribuirPesquisadoresAsTags() {
  const tags = await retomarTags();

  for (const tag of tags) {
    const numeroDePesquisadores = Math.floor(Math.random() * 5) + 1;

    for (let i = 0; i < numeroDePesquisadores; i++) {
      const pesquisador = await retomarPesquisadorAleatorio();
      if (!pesquisador) continue;

      await prisma.researcher_tags_on_researchers.create({
        data: {
          researcher_id: pesquisador.id,
          tag_id: tag.id,
        },
      });
    }
  }
}

atribuirPesquisadoresAsTags();