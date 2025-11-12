import Image from "next/image";
import { Spinner } from '@/components/ui/shadcn-io/spinner';
import { Researcher, TagResult } from "@/types/api";
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

interface TaggedResearchersProps {
  isActive: boolean;
  researchers?: Researcher[];
  isLoadingTagData: boolean;

  tags?: TagResult[];
  onTagChange: (tagName: string) => void;
  currentTag: string | null;
}

export default function TaggedResearchers({
  isActive,
  researchers = [],
  isLoadingTagData,
  tags = [],
  onTagChange,
  currentTag,
}: TaggedResearchersProps) {
  const [selectedChildTag, setSelectedChildTag] = useState<string | null>(null);

  const handleSelectChange = (value: string) => {
    setSelectedChildTag(value);
    onTagChange(value);
  };

  // reseta o filtro de tag filha quando a tag principal mudar
  useEffect(() => {
    const isChild = tags.some(tag => tag.childTags?.includes(currentTag ?? ""));
    if (!isChild) setSelectedChildTag(null);
  }, [currentTag, tags]);

  const selectedTag = tags.find(tag => tag.name === currentTag);

  return (
    <div
      className={`bg-neutral-50 p-3 flex-1 border rounded-md gap-2 flex flex-col h-full ${
        !isActive ? "opacity-50 pointer-events-none" : ""
      }`}
    >
      {isLoadingTagData ? (
        <div className="flex justify-center items-center h-full">
          <Spinner variant="circle" />
        </div>
      ) : (
        <>
          {/* Filtro de tags filhas (só aparece se for tag pai) */}
          <div className="w-full flex justify-end mb-2">
            {selectedTag?.isDadTag && (
              <Select
                value={selectedChildTag ?? ""}
                onValueChange={handleSelectChange}
              >
                <SelectTrigger className="w-fit max-w-[280px] bg-white shadow-sm">
                  <SelectValue placeholder="Filtrar por tag filha..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Tags Encontradas</SelectLabel>
                    {selectedTag.childTags?.map(childTagName => (
                      <SelectItem key={childTagName} value={childTagName}>
                        {childTagName}
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Lista de pesquisadores */}
          <div className="flex flex-wrap gap-3 text-sm overflow-y-auto">
            {researchers.map(researcher => (
              <div
                key={researcher.id}
                className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer"
              >
                <div>
                  <Image
                    className="border border-neutral-300 bg-neutral-200 rounded-md p-1"
                    src="/profile-picture.png"
                    alt="/profile-picture.png"
                    width={40}
                    height={40}
                  />
                </div>
                <div>
                  <p className="">{researcher.name}</p>
                  <div className="bg-eng-blue w-full h-1" />
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
