import { Poppins } from "next/font/google";

const poppinsStrong = Poppins({
  weight: "700",
  subsets: ["latin"],
});

const poppinsWeak = Poppins({
  weight: "500",
  subsets: ["latin"],
});

export default function Home() {
  return (
    <div className="bg-neutral-100 h-screen">
      <main className="h-full flex justify-center items-center">
        <div className="w-full px-36 h-full pt-10 pb-10">
          <div className="w-full h-full border rounded-lg border-neutral-300 bg-neutral-50 flex flex-col">
            <div className="mt-14 w-full px-32 h-56 flex flex-col justify-center items-center gap-10">
              <div className="w-full flex justify-center items-center">
                <p className={`${poppinsStrong.className} text-neutral-800 text-center text-6xl`}>
                  Classificação de Pesquisadores
                </p>
              </div>
              <div className="w-full flex flex-col gap-2">
                {/* Div que contém a caixa de busca */}
                <div className="h-14 rounded-lg border border-neutral-300 w-full shadow"></div>
                {/* Contêiner dos botões: Adicione 'flex' e 'gap-2' para espaçamento */}
                <div className="h-8 w-full flex gap-2">
                  <div className="h-full w-max px-3 bg-blue-400 border rounded-lg flex justify-center items-center">
                    <p className={`text-neutral-50 text-base ${poppinsWeak.className}`}>
                      Inteligência Artificial
                    </p>
                  </div>
                  <div className="h-full w-max px-3 bg-blue-400 border rounded-lg flex justify-center items-center">
                    <p className={`text-neutral-50 text-base ${poppinsWeak.className}`}>
                      Inteligência Emocional
                    </p>
                  </div>
                </div>
              </div> 
            </div>
            <div className="w-full h-full flex-1 pb-10 px-10 flex flex-col">
              <p className={`${poppinsWeak.className} text-neutral-800 text-2xl mb-4`}>
                Pesquisadores
              </p>
              <div className="w-full border rounded-lg border-neutral-300 flex-1">
                
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}