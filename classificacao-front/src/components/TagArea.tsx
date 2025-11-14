import Image from "next/image";
import { Spinner } from "@/components/ui/shadcn-io/spinner";
import { Researcher, TagResult, ResearchersByCategory } from "@/types/api";
import { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X } from "lucide-react";
import { Label } from "@/components/ui/label";

interface TagAreaProps {
  loading: boolean;
  tags: TagResult[];
  onTagClick: (tagName: string) => void;
  selectedTag: string | null;
  allResearchersByCategory: ResearchersByCategory[];
}

export default function TagArea({
  loading,
  tags,
  onTagClick,
  selectedTag,
  allResearchersByCategory,
}: TagAreaProps) {
  const [selectedChildTags, setSelectedChildTags] = useState<string[]>([]);

  // limpa seleção quando muda a tag principal
  useEffect(() => {
    setSelectedChildTags([]);
  }, [selectedTag]);

  const selectedTagObj = tags.find((tag) => tag.name === selectedTag);

  const currentCategory = allResearchersByCategory.find(
    (c) => c.category === selectedTag
  );

  const researchers = currentCategory?.researchers ?? [];

  const unselectedChildTags =
    selectedTagObj?.childTags?.filter(
      (ct) => !selectedChildTags.includes(ct)
    ) || [];

  const handleAddChildTag = (tagName: string) => {
    if (tagName && !selectedChildTags.includes(tagName)) {
      setSelectedChildTags((prev) => [...prev, tagName]);
    }
  };

  const handleRemoveChildTag = (tagName: string) => {
    setSelectedChildTags((prev) => prev.filter((t) => t !== tagName));
  };

  // filtra pesquisadores pelas tags filhas selecionadas (Lógica "E")
  const filteredResearchers = researchers.filter((researcher) => {
    const researcherTags = researcher.tags || [];
    if (selectedChildTags.length === 0) return true;
    
    // Debug Log
    const hasAllTags = selectedChildTags.every((tag) => {
      const hasTag = researcherTags.includes(tag);
      if (!hasTag) {
        console.log(`[FILTRO] REPROVADO: ${researcher.name} não tem a tag "${tag}"`);
      }
      return hasTag;
    });
    
    if (hasAllTags) {
      console.log(`[FILTRO] APROVADO: ${researcher.name} tem todas as tags.`);
    }

    return hasAllTags;
  });

  return (
    <div className="bg-neutral-50 p-3 flex-1 border rounded-md gap-4 flex h-full">
      {/* VISÃO 1: ANTES DE SELECIONAR (tags horizontais) */}
      {selectedTag === null && (
        <div className="flex flex-wrap gap-3 p-2 content-start w-full">
          {loading && (
            <div className="flex justify-center items-center w-full">
              <Spinner variant="circle" />
            </div>
          )}
          {!loading && tags.length === 0 && (
            <p className="text-gray-500">
              Digite na busca para ver as tags...
            </p>
          )}
          {!loading && tags.length > 0 && tags.map((tag) => (
            <button
              key={tag.id}
              onClick={() => onTagClick(tag.name)}
              // 🎨 Botão normal (azul) + cursor
              className="p-2 px-4 bg-eng-blue text-white rounded-md hover:bg-eng-blue-lighted transition-colors cursor-pointer"
            >
              {tag.name}
            </button>
          ))}
        </div>
      )}

      {/* VISÃO 2: DEPOIS DE SELECIONAR (layout da imagem) */}
      {selectedTag !== null && (
        <div className="flex flex-row gap-4 w-full h-full">
          {/* Coluna 1: Lista de Tags (Vertical) */}
          <div className="flex flex-col gap-2 w-1/4 h-full overflow-y-auto">
            {tags.map((tag) => (
              <button
                key={tag.id}
                onClick={() => onTagClick(tag.name)}
                // 🎨 Aplica a cor de seleção + cursor
                className={`p-2 px-4 w-full text-left rounded-md transition-colors cursor-pointer ${
                  tag.name === selectedTag
                    ? "bg-eng-blue-greyed text-white" 
                    : "bg-eng-blue text-white" 
                } hover:bg-eng-blue-lighted`}
              >
                {tag.name}
              </button>
            ))}
          </div>

          {/* Coluna 2: Conteúdo (Pesquisadores e Filtros) */}
          <div className="flex-1 flex flex-col gap-4 h-full">
            {loading ? (
              <div className="flex justify-center items-center h-full">
                <Spinner variant="circle" />
              </div>
            ) : (
              <>
                {/* --- ÁREA DE FILTRO --- */}

                {/* LINHA 1: Cabeçalho (Label e Select) */}
                <div className="w-full flex justify-between items-center">
                  <div> {/* Lado esquerdo para o Label */}
                    {selectedChildTags.length > 0 && (
                      <Label className="text-lg">Tags filhas selecionadas</Label>
                    )}
                  </div>
                  <div> {/* Lado direito para o Select */}
                    {selectedTagObj?.isDadTag && (
                      <Select value="" onValueChange={handleAddChildTag}>
                        <SelectTrigger className="w-fit max-w-[280px] bg-white shadow-sm">
                          <SelectValue placeholder="Filtrar por tags filhas..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectGroup>
                            <SelectLabel>Tags Filhas Disponíveis</SelectLabel>
                            {unselectedChildTags.map((childTagName) => (
                              <SelectItem
                                key={childTagName}
                                value={childTagName}
                              >
                                {childTagName}
                              </SelectItem>
                            ))}
                            {unselectedChildTags.length === 0 && (
                              <SelectItem value="todas" disabled>
                                Todas as tags já foram selecionadas
                              </SelectItem>
                            )}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                </div>

                {/* LINHA 2: Badges (separado) */}
                {selectedChildTags.length > 0 && (
                  <div className="flex flex-wrap gap-3 border-gray-200 rounded-md border p-3">
                    {selectedChildTags.map((tagName) => (
                      <div
                        key={tagName}
                        className="flex w-fit gap-3 items-center border-gray-200 rounded-sm border pr-3 overflow-hidden"
                      >
                        <button
                          className="h-full"
                          onClick={() => handleRemoveChildTag(tagName)}
                        >
                          <div
                            className="flex items-center h-full"
                            title="Remover tag"
                          >
                            <span className="bg-red-200 p-[10px] h-full flex items-center hover:bg-red-400 hover:cursor-pointer hover:text-white transition-all duration-200 ease-in-out">
                              <X className="w-4" />
                            </span>
                          </div>
                        </button>
                        <p className="w-full text-sm">{tagName}</p>
                      </div>
                    ))}
                  </div>
                )}
                {/* --- FIM DA ÁREA DE FILTRO --- */}


                {/* Lista de pesquisadores (scrollable) */}
                <div className="flex-1 flex flex-wrap gap-3 text-sm overflow-y-auto content-start">
                  {filteredResearchers.map((researcher) => (
                    <div
                      key={researcher.id}
                      className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 h-fit hover:bg-neutral-100 cursor-pointer"
                    >
                      <Image
                        className="border border-neutral-300 bg-neutral-200 rounded-md p-1"
                        src="/profile-picture.png"
                        alt="profile-picture"
                        width={40}
                        height={40}
                      />
                      <div>
                        <p className="whitespace-nowrap">{researcher.name}</p>
                        <div className="bg-eng-blue w-full h-1" />
                      </div>
                    </div>
                  ))}

                  {/* Mensagem de filtro sem resultados */}
                  {filteredResearchers.length === 0 &&
                    researchers.length > 0 &&
                    selectedChildTags.length > 0 && (
                      <div className="flex items-center justify-center w-full h-full">
                        <p className="text-gray-500">
                          Nenhum pesquisador encontrado para esta combinação de
                          filtros.
                        </p>
                      </div>
                    )}
                  
                  {/* Mensagem de tag sem pesquisadores */}
                   {researchers.length === 0 && (
                       <div className="flex items-center justify-center w-full h-full">
                        <p className="text-gray-500">
                          Nenhum pesquisador encontrado para esta tag.
                        </p>
                      </div>
                   )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}