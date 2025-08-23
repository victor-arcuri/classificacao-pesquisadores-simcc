"use client";

import { useState, useEffect } from "react";
import { Poppins } from "next/font/google";
import { TagResult } from '../types/api'

const poppinsStrong = Poppins({ weight: "700", subsets: ["latin"] });
const poppinsWeak = Poppins({ weight: "500", subsets: ["latin"] });

export default function Home() {
  const [query, setQuery] = useState("");
  const [categories, setCategories] = useState<TagResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) {
      setCategories([]);
      return;
    }

    const handler = setTimeout(async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/api/search?search=${encodeURIComponent(query)}`);

      if (!res.ok) {
        console.debug("Erro HTTP:", res.status, res.statusText);
        return;
      }

      const data = await res.json();
      console.log(data);
      setCategories(data.results ?? []);
    } catch (err) {
      console.debug("Erro ao buscar categorias", err);
    } finally {
      setLoading(false);
    }
    }, 500);

    return () => clearTimeout(handler);
  }, [query]);

  return (
    <div className="bg-neutral-100 h-screen">
      <main className="h-full flex justify-center items-center">
        <div className="w-full px-36 h-full pt-10 pb-10">
          <div className="w-full h-full border rounded-lg border-neutral-300 bg-neutral-50 flex flex-col">
            <div className="mt-14 w-full px-32 h-56 flex flex-col justify-center items-center gap-10">
              <div className="w-full flex justify-center items-center">
                <p
                  className={`${poppinsStrong.className} text-neutral-800 text-center text-6xl`}
                >
                  Classificação de Pesquisadores
                </p>
              </div>
              <div className="w-full flex flex-col gap-2">
                <div className="h-14 rounded-lg w-full shadow">
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="w-full h-full rounded-lg border border-neutral-300 placeholder-neutral-400 focus:outline-none focus:border-blue-600 text-neutral-800 px-4"
                    placeholder="Digite alguma categoria para iniciar a busca"
                  />
                </div>
                <div className="h-8 w-full flex gap-2 overflow-x-auto">
                  {!loading &&
                    categories.slice(0, 5).map((cat, i) => (
                      <div
                        key={i}
                        className="h-full w-max px-3 bg-blue-400 border rounded-lg flex justify-center items-center"
                      >
                        <p
                          className={`text-neutral-50 text-base ${poppinsWeak.className}`}
                        >
                          {cat.name}
                        </p>
                      </div>
                    ))}
                </div>
              </div>
            </div>
            <div className="w-full h-full flex-1 pb-10 px-10 flex flex-col">
              <p
                className={`${poppinsWeak.className} text-neutral-800 text-2xl mb-4`}
              >
                Pesquisadores
              </p>
              <div className="w-full border rounded-lg border-neutral-300 flex-1"></div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}