"use client";
import { Button } from "@heroui/button";
import { Form } from "@heroui/form";
import { Input, Textarea } from "@heroui/input";
import { addToast } from "@heroui/toast";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { Source_Code_Pro } from "next/font/google";

const sourceCodePro = Source_Code_Pro({
    subsets: ["latin"],
    weight: ["400", "500", "600", "700"]
});

export default function Page() {
    const [sent, setSent] = useState(false);

    const [repo, setRepo] = useState("");
    const [ip, setIp] = useState("");
    const [key, setKey] = useState("");
    const [username, setUsername] = useState("");
    const [envFile, setEnvFile] = useState("");
    const [basePath, setBasePath] = useState(".");
    const [output, setOutput] = useState<{text: string, type: string}[]>([]);
    const ws = useRef<WebSocket | null>(null);
    
    useEffect(() => {
        return () => {
            ws.current?.close();
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setSent(true);

        const data = {
            github_repo: repo,
            hostname: ip,
            username,
            key,
            env_file: envFile,
            base_path: basePath
        }

        try {
            ws.current = new WebSocket("ws://localhost:8000/redeploy");

            const wsc = ws.current;
            
            wsc.onopen = () => {
              console.log('Connected to WebSocket');
              wsc.send(JSON.stringify(data));
            };
    
            wsc.onmessage = (event) => {
                const prs = event.data.replaceAll("'", '"')
                console.log(prs);

                if (prs.startsWith("ERROR:")) {
                    addToast({
                        title: "Error",
                        description: prs,
                        color: "danger"
                    });
                    return;
                }

                if (prs.startsWith("SUCCESS:")) {
                    addToast({
                        title: "Success",
                        description: prs,
                        color: "success"
                    });
                }

                if (prs.startsWith("CMD:")) {
                    setOutput(output => [...output, {
                        text: prs,
                        type: "cmd"
                    }]);
                }

                try {
                    const data = JSON.parse(prs);
    
                    setOutput(output => [...output, {
                        text: data.command,
                        type: "cmd"
                    }]);
                } catch (e) {
                    const data = event.data;
                    setOutput(output => [...output, {
                        text: data,
                        type: "output"
                    }]);
                }
            };
    
            wsc.onclose = () => {
              console.log('WebSocket connection closed');
            };
        } catch (e) {
            addToast({
                title: "Error",
                description: "Unknown error try again.",
                color: "danger"
            });
        }
    }
    
    return (
        <section className="flex">
            {
                !sent ?
                <div className="flex w-full text-center justify-center items-center my-4">
                    <Form onSubmit={handleSubmit} className="flex flex-col items-center justify-center gap-4 w-1/2">
                        <div className="flex flex-col w-full">
                            <label htmlFor="repo" className="w-full text-left">Github Repository</label>
                            <Input 
                            size="lg" 
                            name="repo"
                            placeholder="https://github.com/your-repo" 
                            className="w-full"
                            value={repo}
                            onChange={(e) => setRepo(e.target.value)}
                            />
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="ip" className="w-full text-left">IP Address</label>
                            <Input 
                            size="lg" 
                            name="ip"
                            placeholder="0.0.0.0" 
                            className="w-full"
                            value={ip}
                                onChange={(e) => setIp(e.target.value)}
                            />
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="basePath" className="w-full text-left">Base Path</label>
                            <Input 
                            size="lg" 
                            name="basePath"
                            placeholder="base_path" 
                            className="w-full"
                            value={basePath}
                            onChange={(e) => setBasePath(e.target.value)}
                            />
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="username" className="w-full text-left">Username</label>
                            <Input 
                            size="lg" 
                            name="username"
                            placeholder="username" 
                            className="w-full"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="key" className="w-full text-left">SSH Private Key of sudo user</label>
                            <Textarea
                            size="lg" 
                            name="key"
                            placeholder="-----BEGIN PRIVATE KEY-----"
                            className="w-full"
                                value={key}
                                onChange={(e) => setKey(e.target.value)}
                            />
                        </div>
                        <div className="flex flex-col w-full">
                            <label htmlFor="envFile" className="w-full text-left">Environment File</label>
                            <Textarea
                            size="lg" 
                            name="envFile"
                            placeholder="env_file" 
                            className="w-full"
                                value={envFile}
                                onChange={(e) => setEnvFile(e.target.value)}
                            />
                        </div>
                        <Button size="lg" type="submit" color="primary" className="w-full">
                            Deploy
                        </Button>
                    </Form> 
                </div> :
                <div className={`w-full h-[80vh] mb-8 mx-4 text-center justify-center border-[1px] border-foreground rounded-lg p-4 overflow-y-scroll ${sourceCodePro.className}`}>
                    {
                        output.map((line, index) => (
                            <motion.div 
                                key={index} 
                                className="flex flex-col gap-2"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5 }}
                            >
                                <p className={`${line.type === "cmd" ? "text-blue-500" : "text-green-500"} w-full text-left`}>{line.text}</p>
                            </motion.div>
                        ))
                    }
                </div>
            }
        </section>
    )
}   