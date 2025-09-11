import Image from "next/image";
import { Spinner } from '@/components/ui/shadcn-io/spinner';
import { Researcher } from "@/types/api";

import { useState } from "react";

interface TaggedResearchersProps {
    isActive: boolean;
    researchers?: Researcher[]
    isLoadingTagData: boolean
}

export default function TaggedResearchers({isActive, researchers=[], isLoadingTagData}: TaggedResearchersProps){
    return (
        
        <div className={`bg-neutral-50 p-3 flex-1 ml-2 border rounded-md ${isActive ? '' : 'hidden'} gap-2 flex flex-col`}>
                {isLoadingTagData ? (
                <div className="flex justify-center items-center h-full">
                    <Spinner variant="circle"/>
                </div>
            ) : (
                <div className=" flex flex-wrap gap-3 text-sm">

                  {isActive && researchers.map((researcher) => (
                    <div key={researcher.id} className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
                        <div className="">
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
                            <div className="bg-eng-blue w-full h-1">
                            </div>
                        </div>
                    </div>
                ))}  
                </div>
            )}
        </div>
    );
}