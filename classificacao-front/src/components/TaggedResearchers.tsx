interface TaggedResearchersProps {
    isActive: boolean
}

export default function TaggedResearchers({isActive}: TaggedResearchersProps){
    return (
        <div className={`bg-neutral-50 h-full flex-1 ml-2 border rounded-md ${isActive ? '' : 'hidden'}`}>

        </div>
    );
}