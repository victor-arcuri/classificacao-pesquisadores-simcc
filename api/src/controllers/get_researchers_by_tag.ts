import express, { NextFunction, Request, Response } from "express";
import { searchResearchersByTag } from "../services/searchResearchersByTag.js";

const router = express.Router();

router.get("", async (req: Request, res: Response, next: NextFunction) => {
  const tag = req.query.tag as string;

  if (!tag) {
    return res
      .status(400)
      .json({ error: "Parâmetro de busca 'tag' não pode ser vazio!" });
  }

  try {
    const results = await searchResearchersByTag(tag);
    res.json({ results });
  } catch (error) {
    console.error("Erro na busca:", error);
    res.status(500).json({ error: "Erro interno no servidor" });
  }
});

export default router;