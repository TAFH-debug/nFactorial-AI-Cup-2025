"use client";
import { title } from "@/components/primitives";
import { BackgroundLines } from "@/components/ui/background-lines";
import { Button } from "@heroui/button";
import { Form } from "@heroui/form";
import { Link } from "@heroui/link";
import { motion } from "framer-motion";
import { useSession } from "next-auth/react";
import { useState } from "react";

export default function Home() {
  const session = useSession();
  const [repo, setRepo] = useState("");
  const [ip, setIp] = useState("");
  const [key, setKey] = useState("");
  
  return (
    <section className="flex items-center justify-center">
      <div className="inline-block max-w-2xl text-center justify-center">
      <BackgroundLines className="flex items-center justify-center w-full flex-col px-4">
        <motion.h1 
          className="text-4xl font-bold"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className={`${title({ size: "lg" })}`}>
            Deploy your project in minutes, not hours.
          </span>
        </motion.h1>
        <motion.span 
          className={`text-lg font-light my-4`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          Fast, easy, AI powered deployment for your project.
        </motion.span>
        <Form className="flex flex-row items-center justify-center w-full gap-4">
          <motion.div
            className="relative w-3/4 h-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 to-purple-500/30 rounded-lg blur-xl h-full" />
            <input
              type="text"
              value={repo}
              onChange={(e) => setRepo(e.target.value)} 
              placeholder="https://github.com/your-repo"
              className="w-full px-4 py-2 bg-white/10 h-full backdrop-blur-sm rounded-lg border text-foreground placeholder:text-foreground/50 outline-none border-none focus:outline-none"
            />
          </motion.div>
          <motion.div
            className="relative w-1/4 h-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Button size="lg" color="primary" className="w-full" as={Link} href="/deploy">
              Deploy
            </Button>
          </motion.div>
        </Form>
      </BackgroundLines>
      </div>
    </section>

  );
}
