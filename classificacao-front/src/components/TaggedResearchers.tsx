interface TaggedResearchersProps {
    isActive: boolean
}

export default function TaggedResearchers({isActive}: TaggedResearchersProps){
    return (
        <div className={`bg-neutral-50 p-6 flex-1 ml-2 border rounded-md ${isActive ? '' : 'hidden' } flex-wrap`}>
            {
                isActive && null
            }
        </div>
    );
}