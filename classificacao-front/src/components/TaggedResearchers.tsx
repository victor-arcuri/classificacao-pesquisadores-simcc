import Image from "next/image";
import { Researcher } from "@/types/api";

import { useState } from "react";

interface TaggedResearchersProps {
    isActive: boolean;
    researchers?: Researcher[]
}

export default function TaggedResearchers({isActive, researchers=[]}: TaggedResearchersProps){


    return (
        <div className={`bg-neutral-50 p-3 flex-1 ml-2 border rounded-md ${isActive ? '' : 'hidden'} gap-2 flex flex-col`}>
                {/*
                <div className=" flex flex-wrap gap-3 text-sm">
                    <div className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
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
                        <p className=""> Carlos Augusto da Silveira</p>
                        <div className="bg-eng-blue w-full h-1">
                        </div>
                    </div>
                    </div>
                    <div className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
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
                            <p className=""> Jośe Hugo da Silva</p>
                            <div className="bg-eng-blue w-full h-1">
                            </div>
                        </div>
                    </div>
                    <div className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
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
                            <p className=""> João Oliveira Campos </p>
                            <div className="bg-eng-blue w-full h-1">
                            </div>
                        </div>
                    </div>
                    <div className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
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
                            <p className=""> Emanuel Carvalho Gomes</p>
                            <div className="bg-eng-blue w-full h-1">
                            </div>
                        </div>
                    </div>
                </div>
                */}
                {isActive && researchers.map((researcher) => (
                    <div key={researcher.name} className="border font-sans flex rounded-md items-center gap-2 w-fit p-2 hover:bg-neutral-100 cursor-pointer">
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
                {/*<div className="flex justify-center">
                    <div className="border roundes-sm bg-eng-blue w-fit h-fit px-4 rounded-md justify-center items-center">
                        <p className="text-xl font-bold text-neutral-50 text-center">
                        +
                        </p>
                    </div>
                </div>*/}
        
                
                
                
            
        </div>
    );
}