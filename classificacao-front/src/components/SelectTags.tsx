import * as React from "react"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function SelectTags() {
  return (
    <div className="flex justify-center self-start pt-6 w-full">
      <Select>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Selecione uma fruta" />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            <SelectLabel>Filtrar Tags</SelectLabel>
            <SelectItem value="apple">Apple</SelectItem>
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  )
}