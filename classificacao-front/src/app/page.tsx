"use client";

import HeroSection from "@/components/HeroSection";
import SearchBar from "@/components/SearchBar";
import TagArea from "@/components/TagArea";
import { ResearchersByCategory, TagResult, SearchResponse } from "@/types/api";
import { useState, useEffect } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [tags, setTags] = useState<TagResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [allResearchersByCategory, setAllResearchersByCategory] = useState<ResearchersByCategory[]>([]);

  const selectTag = (tagName: string) => {
    if (selectedTag === tagName) { // Clicou na tag que já estava selecionada = função de desmarcar
      setSelectedTag(null);
      return;
    }

    if (selectedTag === null) {
      const tagToMove = tags.find(tag => tag.name === tagName);

      if (tagToMove) {
        const otherTags = tags.filter(tag => tag.name !== tagName);
        setTags([tagToMove, ...otherTags]);
      }
    }

    setSelectedTag(tagName);
  };

  // Busca de tags
  useEffect(() => {
    // se a busca estiver vazia, limpa tudo e para
    if (query.trim() === "") {
      setTags([]);
      setSelectedTag(null); 
      setLoading(false);
      return;
    }

    setLoading(true); 

    // Debounce
    const handler = setTimeout(async () => {
      // Limpa a seleção anterior ANTES de buscar novas tags
      setSelectedTag(null); 
      
      try {
        const res = await fetch(`http://localhost:3001/api/search?search=${encodeURIComponent(query)}`);

        if (!res.ok) {
          console.debug("Erro HTTP ao buscar tags:", res.status, res.statusText);
          setTags([]); 
          return;
        }

        const data: SearchResponse = await res.json();
        setTags(data.results);
      } catch (err) {
        console.debug("Erro ao buscar tags", err);
        setTags([]); 
      } finally {
        setLoading(false); // desativa o spinner
      }
    }, 300); 

    return () => clearTimeout(handler);

  }, [query]); 

  // Busca de pesquisadores pela tag selecionada
  useEffect(() => {
    console.log("🟢 useEffect [selectedTag] rodou:", selectedTag);

    if (selectedTag == null) return;

    const isAlreadyCached = allResearchersByCategory.find(item => item.category === selectedTag);

    if (isAlreadyCached) {
      console.log("⚪ Já tem cache para:", selectedTag);
      setLoading(false);
      return;
    }

    setLoading(true);
    const handler = setTimeout(async () => {
      console.log("🟡 Buscando pesquisadores para:", selectedTag);
      try {
        const res = await fetch(`http://localhost:3001/api/researchers?tag=${encodeURIComponent(selectedTag)}`);

        if (!res.ok) {
          console.debug("❌ Erro HTTP:", res.status, res.statusText);
          return;
        }

        const data = await res.json();
        console.log("✅ Dados recebidos da API:", data);

        setAllResearchersByCategory(prevData => [
          ...prevData,
          {
            category: selectedTag,
            researchers: data
          }
        ]);
      } catch (err) {
        console.debug("⚠️ Erro ao buscar pesquisadores da tag especificada", err);
      }
      finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(handler);
  }, [selectedTag]); 

  return (
    <div className="bg-neutral-100 h-screen p-6">
      <div className="h-full mx-36 bg-neutral-50 p-2 rounded-xl flex flex-col border">
        <div className="h-56 pt-2">
          <HeroSection />
        </div>

        <div className="px-12 mt-6">
          <SearchBar onChange={(e) => setQuery(e.target.value)} value={query} />
        </div>

        <div className="px-12 flex-1 p-3 min-h-0">
          <TagArea
            loading={loading}
            tags={tags}
            onTagClick={selectTag}
            selectedTag={selectedTag}
            allResearchersByCategory={allResearchersByCategory}
          />
        </div>
      </div>
    </div>
  );
}