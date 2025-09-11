export interface TagResult {
  id: string;
  name: string;
  ts_score: number;
  trgm_score: number;
}

export interface SearchResponse {
  results: TagResult[];
}

export interface Researcher {
  id: string;
  name: string;
}

export interface ResearchersByCategory{
  category: string
  researchers: Researcher[]
}