import DeployForm from "@/components/deploy-form";

export default function Page() {
    return (
        <section className="flex">
            <div className="inline-block w-1/2 text-center justify-center">
                <DeployForm />
            </div>
            <div className="inline-block w-1/2 text-center justify-center">
                <h1>Deploying...</h1>
            </div>
        </section>
    )
}