REATE TEXT SEARCH CONFIGURATION portuguese_unaccent (
  COPY = portuguese
);

ALTER TEXT SEARCH CONFIGURATION portuguese_unaccent
ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, hword, hword_part, word WITH unaccent, portuguese_stem;