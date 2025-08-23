import { searchTag } from "../services/fullTextSearch.js";
import express, { NextFunction, Request, Response } from "express";

const router = express.Router();

router.get("", async (req: Request, res: Response, next: NextFunction) => {
  const search = req.query.search as string;

  if (!search) {
    return res
      .status(400)
      .json({ error: "Parâmetro de busca 'search' não pode ser vazio!" });
  }

  try {
    const results = await searchTag(search);
    res.json({ results });
  } catch (error) {
    console.error("Erro na busca:", error);
    res.status(500).json({ error: "Erro interno no servidor" });
  }
});

export default router;