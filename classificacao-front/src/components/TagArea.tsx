import { useState } from "react";
import Tag from "./Tag";
import TaggedResearchers from "./TaggedResearchers";
import { TagResult } from "@/types/api";


interface TagAreaProps {
    loading?: boolean,
    tags?: TagResult[],
    onTagClick: (tagName: string) => void,
    selectedTag: null | string
}


export default function TagArea({loading=false, tags=[], onTagClick, selectedTag}: TagAreaProps){

    return (
        <div 
            className={`
            ${selectedTag != null ? 
                'w-full h-full flex p-2 gap-3 content-start flex-col bg-neutral-100 border rounded-xl  overflow-y-auto' 
                : 
                'w-full h-full flex p-2 gap-3 content-start flex-wrap'}
            `}
        >
            {!loading && tags.map((tag) => (
                <div className="flex" key={tag.name}>
                    <Tag tagText={tag.name} onTagClick={onTagClick} selected={selectedTag === tag.name} />
                    <TaggedResearchers isActive={selectedTag === tag.name} />
                </div>
            ))}
        
        </div>
    );
}