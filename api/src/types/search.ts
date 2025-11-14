export interface MatchingTag {
    id: string;
    name: string;
    isDadTag: boolean;
    ts_score: number;
    trgm_score: number;
    childTags: string[];
}