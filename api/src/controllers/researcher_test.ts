import express, { NextFunction, Request, Response } from "express";

const router = express.Router();

router.get("", async (req: Request, res: Response, next: NextFunction) => {

  try {
    const results = [
  {
    "id": "e4a2b1e2-5b3c-4d1a-8e7f-9c0b1a2b3c4d",
    "name": "Lucas Martins Pereira"
  },
  {
    "id": "f8c3b2a1-6d4e-4f2b-9a8c-7b6a5e4d3c2b",
    "name": "Juliana Costa e Silva"
  },
  {
    "id": "a1b2c3d4-8e7f-4a9b-8c6d-5e4f3a2b1c0d",
    "name": "Rafael Oliveira Souza"
  },
  {
    "id": "c7d6e5f4-3a2b-4c1d-9e8f-7b6a5d4c3b2a",
    "name": "Beatriz Almeida Rodrigues"
  },
  {
    "id": "b4a3c2d1-9e8f-4b1a-8d7c-6e5f4a3b2c1d",
    "name": "Gabriel Ferreira Lima"
  },
  {
    "id": "d9e8f7a6-5b4c-4d3e-a1b2-c3d4e5f6a7b8",
    "name": "Mariana Gonçalves Alves"
  },
  {
    "id": "a3b2c1d0-9e8f-4a1b-8c7d-6e5f4a3b2c1d",
    "name": "Thiago Santos Ribeiro"
  },
  {
    "id": "f1e2d3c4-7b6a-4e5f-9a8b-7c6d5e4f3a2b",
    "name": "Camila Barbosa Azevedo"
  },
  {
    "id": "c8d7e6f5-4a3b-4c2d-9e1f-8b7a6d5c4b3a",
    "name": "Fernando Correia Mendes"
  },
  {
    "id": "b5a4c3d2-1e9f-4b8a-8d7c-6e5f4a3b2c1d",
    "name": "Isabela Rocha Nogueira"
  }
] 
    res.json(results);
  } catch (error) {
    console.error("Erro na busca:", error);
    res.status(500).json({ error: "Erro interno no servidor" });
  }
});

export default router;