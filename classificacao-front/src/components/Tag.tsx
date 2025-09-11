interface TagProps {
    tagText?: string
    selected?: boolean,
    onTagClick: (tagName: string) => void
}

export default function Tag({tagText="", selected=false, onTagClick}: TagProps){
    return (
        <div onClick={()=>onTagClick(tagText)} className={`${selected? 'bg-eng-blue-greyed' : 'bg-eng-blue'} h-10 w-40 text-white flex items-center justify-center rounded ${selected? '' : 'hover:bg-eng-blue-lighted'}`}>
            <p className="text-center text-sm font-bold font-sans">
                {tagText}
            </p>
        </div>
    );
}