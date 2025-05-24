"use client";
import { Snippet } from "@heroui/snippet";
import { Code } from "@heroui/code";

import { title } from "@/components/primitives";
import { useSession } from "next-auth/react";

export default function Home() {
  const session = useSession();
  
  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
      <div className="inline-block max-w-xl text-center justify-center">
        <span className={title()}>
          Next.JS + HeroUI + DrizzleORM + Neon template
        </span>
      </div>

      <div className="mt-8">
        <Snippet hideCopyButton hideSymbol variant="bordered">
          <span>
            Get started by editing <Code color="primary">app/page.tsx</Code>
          </span>
        </Snippet>
      </div>
    </section>
  );
}
