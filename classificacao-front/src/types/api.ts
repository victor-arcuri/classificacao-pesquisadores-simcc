export interface TagResult {
  id: string;
  name: string;
  ts_score: number;
  trgm_score: number;
}

export interface SearchResponse {
  results: TagResult[];
}