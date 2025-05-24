"use client";

import { Button } from "@heroui/button";
import { Form } from "@heroui/form";
import { Input, Textarea } from "@heroui/input";
import { useState } from "react";
import axios from "axios";

export default function DeployForm() {
    const [repo, setRepo] = useState("");
    const [ip, setIp] = useState("");
    const [key, setKey] = useState("");
    const [username, setUsername] = useState("");
    const [envFile, setEnvFile] = useState("");

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const response = await axios.post("http://localhost:8000/deploy", {
            github_repo: repo,
            hostname: ip,
            username,
            key,
            env_file: envFile,
        });
        console.log(response.data);
    }
    
    return (
        <Form onSubmit={handleSubmit} className="flex flex-col items-center justify-center gap-4">
            <div className="flex flex-col w-full">
                <label htmlFor="repo" className="w-full text-left">Github Repository</label>
                <Input 
                size="lg" 
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
                placeholder="0.0.0.0" 
                className="w-full"
                value={ip}
                    onChange={(e) => setIp(e.target.value)}
                />
            </div>
            <div className="flex flex-col w-full">
                <label htmlFor="username" className="w-full text-left">Username</label>
                <Input 
                size="lg" 
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
    )
}   