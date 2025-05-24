"use client";
import { useSession, signIn } from "next-auth/react";
import { FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@heroui/button";
import { Form } from "@heroui/form";
import { Input } from "@heroui/input";

export default function SignIn() {
  const router = useRouter();
  const { data: session } = useSession();

  useEffect(() => {
    if (session) {
      router.push("/");
    }
  }, [session]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    await signIn("credentials", {
      email,
      password,
      redirect: false,
      signup: true,
    });

    router.push("/");
    router.refresh();
  };

  return (
    <Form className="justify-center items-center" onSubmit={handleSubmit}>
      <div className="flex flex-col max-w-md gap-4">
        <Input name="email" placeholder="Email" />
        <Input name="password" placeholder="Password" type="password" />
        <Button type="submit">Send</Button>
      </div>
    </Form>
  );
}
