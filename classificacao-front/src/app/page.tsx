"use client";

import HeroSection from "@/components/HeroSection";
import SearchBar from "@/components/SearchBar";
import TagArea from "@/components/TagArea";
import { ResearchersByCategory, TagResult } from "@/types/api";

import { useState, useEffect } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [tags, setTags] = useState<TagResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [allResearchersByCategory, setAllResearchersByCategory] = useState<ResearchersByCategory[]>([]);
  
  const selectTag = (tagName: string) => {
    if (selectedTag == tagName){
      setSelectedTag(null);
      return;
    }
    if (selectedTag == null){
      const tagToMove = tags.find(tag => tag.name === tagName);

      if (tagToMove) {
        const otherTags = tags.filter(tag => tag.name !== tagName);
      
        setTags([tagToMove, ...otherTags]);
      }
    }
    setSelectedTag(tagName);
  }

    useEffect(() => {
    if (selectedTag == null) return;

    const isAlreadyCached = allResearchersByCategory.find(item => item.category === selectedTag);

    if (isAlreadyCached) {
      setLoading(false);
      return; 
    }

    setLoading(true);
    const handler = setTimeout(async () => {
      try {
        const res = await fetch(`http://localhost:5000/api/teste/`);

        if (!res.ok) {
          console.debug("Erro HTTP:", res.status, res.statusText);
          return;
        }

        const data = await res.json();

        setAllResearchersByCategory(prevData => [
          ...prevData,
          {
            "category": selectedTag,
            "researchers": data
          }
        ]);

      } catch (err) {
        console.debug("Erro ao buscar pesquisadores da tag especificada", err);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(handler);

  }, [selectedTag, allResearchersByCategory]);

  
  useEffect(() => {
    if (!query) {
      setTags([]);
      setSelectedTag(null);
      return;
    }


    setSelectedTag(null);
    const handler = setTimeout(async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/api/search?search=${encodeURIComponent(query)}`);
  
      if (!res.ok) {
        console.debug("Erro HTTP:", res.status, res.statusText);
        return;
      }
  
      const data = await res.json();

      setTags(data.results ?? []);
    } catch (err) {
      console.debug("Erro ao buscar categorias", err);
    } finally {
      setLoading(false);
    }
    }, 500);
    return () => clearTimeout(handler);
  }, [query]);

  return (
    <div className="bg-neutral-100 h-screen p-6 ">
      <div className="h-full mx-36 bg-neutral-50 p-2 rounded-xl flex flex-col border">
        <div className="h-56 pt-2">
          <HeroSection/>
        </div>
        <div className="px-12 mt-6">
          <SearchBar onChange={(e)=> setQuery(e.target.value)} value={query}/>
        </div>

        <div className="px-12 flex-1 p-3 min-h-0">
          <TagArea loading={loading} tags={tags} onTagClick={selectTag} selectedTag={selectedTag} allResearchersByCategory={allResearchersByCategory}/>
        </div>
      </div>
    </div>
  );
}