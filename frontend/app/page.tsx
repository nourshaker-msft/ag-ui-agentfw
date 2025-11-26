import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
      <div className="max-w-4xl mx-auto p-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Agent Framework + CopilotKit
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-2">
            Full-stack agentic chat with AG-UI integration
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Microsoft Agent Framework • CopilotKit • Next.js • FastAPI
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <AgentCard
            href="/chat/simple"
            title="Simple Chat"
            description="General purpose AI assistant for conversations"
            icon="💬"
            color="blue"
          />
          <AgentCard
            href="/chat/weather"
            title="Weather Agent"
            description="Get weather information with beautiful UI rendering"
            icon="🌤️"
            color="indigo"
          />
          <AgentCard
            href="/chat/tasks"
            title="Task Planner"
            description="Plan and execute tasks with human oversight"
            icon="✅"
            color="purple"
          />
          <AgentCard
            href="/chat/shared_state"
            title="Recipe Assistant"
            description="Create and improve recipes with AI assistance"
            icon="👨‍🍳"
            color="green"
          />
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-semibold mb-4">Features</h2>
          <ul className="space-y-3">
            <Feature text="🚀 Real-time streaming responses" />
            <Feature text="🎨 Beautiful UI with backend tool rendering" />
            <Feature text="🤝 Human-in-the-loop interactions" />
            <Feature text="🔄 State management and predictive updates" />
            <Feature text="🌓 Dark mode support" />
            <Feature text="⚡ Built with modern tech stack" />
          </ul>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            Powered by{" "}
            <a
              href="https://github.com/microsoft/agent-framework"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Microsoft Agent Framework
            </a>{" "}
            and{" "}
            <a
              href="https://copilotkit.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:underline"
            >
              CopilotKit
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

function AgentCard({
  href,
  title,
  description,
  icon,
  color,
}: {
  href: string;
  title: string;
  description: string;
  icon: string;
  color: "blue" | "indigo" | "purple" | "green";
}) {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
    indigo: "from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700",
    purple: "from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700",
    green: "from-green-500 to-green-600 hover:from-green-600 hover:to-green-700",
  };

  return (
    <Link href={href}>
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer h-full">
        <div
          className={`w-12 h-12 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center text-2xl mb-4`}
        >
          {icon}
        </div>
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm">{description}</p>
      </div>
    </Link>
  );
}

function Feature({ text }: { text: string }) {
  return (
    <li className="flex items-center text-gray-700 dark:text-gray-300">
      <span className="mr-2">•</span>
      {text}
    </li>
  );
}
