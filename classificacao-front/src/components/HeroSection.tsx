import { WavyBackground } from "@/components/ui/shadcn-io/wavy-background";
import { memo } from "react";

function HeroSection() {
  return (
    <div className="relative h-full w-full overflow-hidden mb-1 rounded-xl">
      <WavyBackground
        backgroundFill="#fafafa"
        colors={["#76abc4", "#cececf"]}
        waveWidth={20}
        blur={10}
        speed="fast"
        waveOpacity={0.3}
        containerClassName="h-full w-full"
        className="flex items-center justify-center w-full h-full"
      >
        <div className="flex w-full h-full flex-col justify-center"> 
            <div className={`text-center text-black font-bold z-10 w-full`}>
                <h1 className={`font-sans text-6xl font-bold`}>
                    Classificação de Pesquisadores
                </h1>
            </div>
        </div>
      </WavyBackground>
    </div>
  );
}

export default memo(HeroSection);