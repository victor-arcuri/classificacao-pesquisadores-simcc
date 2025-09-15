import { Input } from "@/components/ui/input"
import { ChangeEvent } from "react";

interface SearchBarProps {
    onChange?: (event: ChangeEvent<HTMLInputElement>) => void;
    value?: string
}

export default function SearchBar({onChange, value}: SearchBarProps){
    return (
        <div className="w-full rounded-lg shadow h-12">
            <Input className="font-sans bg-neutral-50 h-12 border-1" placeholder="Digite alguma categoria para iniciar a busca" onChange={onChange} value={value}/>
        </div>
    );
}