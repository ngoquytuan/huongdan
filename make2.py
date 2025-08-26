#!/usr/bin/env python3
"""
Next.js Template Generator with Docker
Tạo cấu trúc thư mục chuẩn cho dự án Next.js với TypeScript và Docker
"""

import os
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Any

class NextJSTemplateGenerator:
    def __init__(self, project_name: str = "my-nextjs-template"):
        self.project_name = project_name
        self.base_path = Path(project_name)

    # ===================================================================
    # 1. Cấu trúc thư mục và file Core
    # ===================================================================

    def create_directory_structure(self):
        """Tạo cấu trúc thư mục"""
        directories = [
            ".vscode",
            "public/icons", "public/images",
            "src/app/(main)", "src/app/api/example",
            "src/components/shared", "src/components/ui",
            "src/contexts", "src/hooks", "src/lib", "src/types",
        ]
        print(f"🚀 Tạo dự án Next.js: {self.project_name}")
        self.base_path.mkdir(exist_ok=True)
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Tạo thư mục: {directory}")
        
        gitkeep_dirs = [
            "public/icons", "public/images", "src/components/shared", "src/contexts"
        ]
        for directory in gitkeep_dirs:
            (self.base_path / directory / ".gitkeep").touch()

    def create_package_json(self):
        """Tạo package.json với dependencies cần thiết"""
        package_json = {
            "name": self.project_name, "version": "0.1.0", "private": True,
            "scripts": {
                "dev": "next dev", "build": "next build", "start": "next start",
                "lint": "next lint", "lint:fix": "next lint --fix",
                "type-check": "tsc --noEmit",
                "docker:dev": "docker-compose up --build",
                "docker:prod": "docker-compose -f docker-compose.prod.yml up --build"
            },
            "dependencies": {
                "axios": "^1.6.0", "clsx": "^2.0.0", "lucide-react": "^0.294.0",
                "next": "^14.0.0", "react": "^18.0.0", "react-dom": "^18.0.0",
                "tailwind-merge": "^2.0.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0", "@types/react": "^18.0.0", "@types/react-dom": "^18.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0", "@typescript-eslint/parser": "^6.0.0",
                "autoprefixer": "^10.0.0", "eslint": "^8.0.0", "eslint-config-next": "^14.0.0",
                "postcss": "^8.0.0", "prettier": "^3.0.0", "tailwindcss": "^3.0.0",
                "typescript": "^5.0.0"
            }
        }
        with open(self.base_path / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
        print("📦 Tạo package.json")

    # ===================================================================
    # 2. Các file cấu hình
    # ===================================================================

    def create_typescript_config(self):
        """Tạo tsconfig.json"""
        tsconfig = {
            "compilerOptions": {
                "target": "es5", "lib": ["dom", "dom.iterable", "es6"], "allowJs": True,
                "skipLibCheck": True, "strict": True, "noEmit": True, "esModuleInterop": True,
                "module": "esnext", "moduleResolution": "bundler", "resolveJsonModule": True,
                "isolatedModules": True, "jsx": "preserve", "incremental": True,
                "plugins": [{"name": "next"}],
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"],
                    "@/components/*": ["./src/components/*"],
                    "@/lib/*": ["./src/lib/*"],
                    "@/types/*": ["./src/types/*"],
                    "@/hooks/*": ["./src/hooks/*"],
                    "@/contexts/*": ["./src/contexts/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        with open(self.base_path / "tsconfig.json", "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)
        print("⚙️  Tạo tsconfig.json")

    def create_nextjs_config(self):
        """Tạo next.config.mjs"""
        config_content = '''/** @type {import('next').NextConfig} */\nconst nextConfig = {\n  // Cấu hình cho Docker\n  output: 'standalone',\n};\n\nexport default nextConfig;\n'''
        with open(self.base_path / "next.config.mjs", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("⚙️  Tạo next.config.mjs")

    def create_tailwind_config(self):
        """Tạo tailwind.config.ts"""
        config_content = '''import type { Config } from 'tailwindcss'\n\nconst config: Config = {\n  content: [\n    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',\n    './src/components/**/*.{js,ts,jsx,tsx,mdx}',\n    './src/app/**/*.{js,ts,jsx,tsx,mdx}',\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n\nexport default config\n'''
        with open(self.base_path / "tailwind.config.ts", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("🎨 Tạo tailwind.config.ts")

    def create_postcss_config(self):
        """Tạo postcss.config.js"""
        postcss_content = '''module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n'''
        with open(self.base_path / "postcss.config.js", "w", encoding="utf-8") as f:
            f.write(postcss_content)
        print("🎨 Tạo postcss.config.js")

    def create_eslint_config(self):
        """Tạo .eslintrc.json"""
        eslint_config = {"extends": "next/core-web-vitals"}
        with open(self.base_path / ".eslintrc.json", "w", encoding="utf-8") as f:
            json.dump(eslint_config, f, indent=2)
        print("🔍 Tạo .eslintrc.json")

    def create_prettier_config(self):
        """Tạo .prettierrc"""
        prettier_config = {"semi": True, "trailingComma": "es5", "singleQuote": True, "printWidth": 80, "tabWidth": 2}
        with open(self.base_path / ".prettierrc", "w", encoding="utf-8") as f:
            json.dump(prettier_config, f, indent=2)
        print("💅 Tạo .prettierrc")

    def create_vscode_settings(self):
        """Tạo VS Code settings"""
        settings = {
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {"source.fixAll.eslint": "explicit"},
        }
        with open(self.base_path / ".vscode/settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        print("🔧 Tạo VS Code settings")

    # ===================================================================
    # 3. Docker
    # ===================================================================

    def create_docker_files(self):
        """Tạo Dockerfile và docker-compose.yml"""
        dockerfile_content = '''FROM node:20-alpine AS base\n\n# Install dependencies only when needed\nFROM base AS deps\nWORKDIR /app\nCOPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./\nRUN \\\n  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \\\n  elif [ -f package-lock.json ]; then npm ci; \\\n  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \\\n  else echo "Lockfile not found." && exit 1; \\\n  fi\n\n# Rebuild the source code only when needed\nFROM base AS builder\nWORKDIR /app\nCOPY --from=deps /app/node_modules ./node_modules\nCOPY . .\nENV NEXT_TELEMETRY_DISABLED 1\nRUN npm run build\n\n# Production image, copy all the files and run next\nFROM base AS runner\nWORKDIR /app\nENV NODE_ENV production\nENV NEXT_TELEMETRY_DISABLED 1\nRUN addgroup --system --gid 1001 nodejs\nRUN adduser --system --uid 1001 nextjs\nCOPY --from=builder /app/public ./public\nRUN mkdir .next\nRUN chown nextjs:nodejs .next\nCOPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./\nCOPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static\nUSER nextjs\nEXPOSE 3000\nENV PORT 3000\nCMD ["node", "server.js"]\n'''
        with open(self.base_path / "Dockerfile", "w", encoding="utf-8") as f: f.write(dockerfile_content)
        
        docker_compose_content = '''version: '3.8'\nservices:\n  nextjs-app:\n    container_name: nextjs-dev\n    build:\n      context: .\n      dockerfile: Dockerfile\n    ports:\n      - "3000:3000"\n    volumes:\n      - .:/app\n      - /app/node_modules\n      - /app/.next\n    environment:\n      - NODE_ENV=development\n    command: npm run dev\n    restart: unless-stopped\n'''
        with open(self.base_path / "docker-compose.yml", "w", encoding="utf-8") as f: f.write(docker_compose_content)
        
        docker_compose_prod_content = '''version: '3.8'\nservices:\n  nextjs-app:\n    container_name: nextjs-prod\n    build:\n      context: .\n      dockerfile: Dockerfile\n    ports:\n      - "3000:3000"\n    environment:\n      - NODE_ENV=production\n    restart: unless-stopped\n'''
        with open(self.base_path / "docker-compose.prod.yml", "w", encoding="utf-8") as f: f.write(docker_compose_prod_content)
        print("🐳 Tạo Docker files")

    # ===================================================================
    # 4. App files và CSS
    # ===================================================================

    def create_app_files(self):
        """Tạo các file chính của Next.js App"""
        root_layout = '''import type { Metadata } from 'next'\nimport { Inter } from 'next/font/google'\nimport './globals.css'\n\nconst inter = Inter({ subsets: ['latin'] })\n\nexport const metadata: Metadata = {\n  title: 'My Next.js App',\n  description: 'Generated by a custom script',\n}\n\nexport default function RootLayout({ children }: { children: React.ReactNode }) {\n  return (\n    <html lang="en">\n      <body className={inter.className}>{children}</body>\n    </html>\n  )\n}\n'''
        with open(self.base_path / "src/app/layout.tsx", "w", encoding="utf-8") as f: f.write(root_layout)
        
        main_layout = '''import { Header } from '@/components/shared/header'\nimport { ReactNode } from 'react'\n\nexport default function MainLayout({ children }: { children: ReactNode }) {\n  return (\n    <div className="flex min-h-screen flex-col">\n      <Header />\n      <main className="flex-1 container mx-auto px-4 py-8">{children}</main>\n    </div>\n  )\n}\n'''
        with open(self.base_path / "src/app/(main)/layout.tsx", "w", encoding="utf-8") as f: f.write(main_layout)
        
        home_page = '''export default function HomePage() {\n  return (\n    <div className="text-center">\n      <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">Welcome to Your App</h1>\n      <p className="mt-6 text-lg leading-8 text-gray-600">This is a template generated by a custom Python script.</p>\n    </div>\n  )\n}\n'''
        with open(self.base_path / "src/app/(main)/page.tsx", "w", encoding="utf-8") as f: f.write(home_page)
        print("📄 Tạo App files")

    def create_css_files(self):
        """Tạo CSS files"""
        globals_css = '''@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n@layer base {\n  body {\n    @apply min-h-screen bg-background text-foreground;\n  }\n}\n'''
        with open(self.base_path / "src/app/globals.css", "w", encoding="utf-8") as f: f.write(globals_css)
        print("🎨 Tạo CSS files")

    # ===================================================================
    # 5. Thư viện code (lib)
    # ===================================================================

    def create_lib_files(self):
        """Tạo các file trong thư mục lib"""
        api_client = '''import axios from 'axios'\n\nconst apiClient = axios.create({\n  baseURL: process.env.NEXT_PUBLIC_API_URL,\n  headers: { 'Content-Type': 'application/json' },\n});\n\n// Add interceptors if needed\n\nexport default apiClient;\n'''
        with open(self.base_path / "src/lib/api.ts", "w", encoding="utf-8") as f: f.write(api_client)

        utils_content = '''import { type ClassValue, clsx } from 'clsx'\nimport { twMerge } from 'tailwind-merge'\n\nexport function cn(...inputs: ClassValue[]) {\n  return twMerge(clsx(inputs))\n}\n'''
        with open(self.base_path / "src/lib/utils.ts", "w", encoding="utf-8") as f: f.write(utils_content)

        api_service = '''import apiClient from './api'\nimport { User, ApiResponse } from '@/types'\n\nexport const userApi = {\n  getUsers: async (): Promise<User[]> => {\n    const response = await apiClient.get<ApiResponse<User[]>>('/users');\n    return response.data.data;\n  },\n};\n'''
        with open(self.base_path / "src/lib/services.ts", "w", encoding="utf-8") as f: f.write(api_service)
        print("📚 Tạo lib files")
        
    def create_types_file(self):
        """Tạo file types"""
        types_content = '''export interface User {\n  id: string;\n  name: string;\n  email: string;\n}\n\nexport interface ApiResponse<T> {\n  data: T;\n  success: boolean;\n  message?: string;\n}\n'''
        with open(self.base_path / "src/types/index.d.ts", "w", encoding="utf-8") as f: f.write(types_content)
        print("🔤 Tạo types file")

    # ===================================================================
    # 6. Các file code mẫu
    # ===================================================================

    def create_sample_components(self):
        """Tạo các component mẫu"""
        button_component = '''import * as React from 'react'\nimport { Slot } from '@radix-ui/react-slot'\nimport { cva, type VariantProps } from 'class-variance-authority'\nimport { cn } from '@/lib/utils'\n\nconst buttonVariants = cva(\n  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',\n  {\n    variants: {\n      variant: {\n        default: 'bg-primary text-primary-foreground hover:bg-primary/90',\n        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',\n        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',\n        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',\n        ghost: 'hover:bg-accent hover:text-accent-foreground',\n        link: 'text-primary underline-offset-4 hover:underline',\n      },\n      size: {\n        default: 'h-10 px-4 py-2',\n        sm: 'h-9 rounded-md px-3',\n        lg: 'h-11 rounded-md px-8',\n        icon: 'h-10 w-10',\n      },\n    },\n    defaultVariants: {\n      variant: 'default',\n      size: 'default',\n    },\n  }\n)\n\nexport interface ButtonProps\n  extends React.ButtonHTMLAttributes<HTMLButtonElement>,\n    VariantProps<typeof buttonVariants> {\n  asChild?: boolean\n}\n\nconst Button = React.forwardRef<HTMLButtonElement, ButtonProps>(\n  ({ className, variant, size, asChild = false, ...props }, ref) => {\n    const Comp = asChild ? Slot : 'button'\n    return (\n      <Comp\n        className={cn(buttonVariants({ variant, size, className }))}\n        ref={ref}\n        {...props}\n      />\n    )\n  }\n)\nButton.displayName = 'Button'\n\nexport { Button, buttonVariants }\n'''
        with open(self.base_path / "src/components/ui/button.tsx", "w", encoding="utf-8") as f: f.write(button_component)
        
        header_component = '''import Link from 'next/link'\n\nexport function Header() {\n  return (\n    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">\n      <div className="container flex h-14 items-center">\n        <Link href="/" className="mr-6 flex items-center space-x-2">\n          <span className="font-bold">MyApp</span>\n        </Link>\n        <nav className="flex items-center space-x-4 lg:space-x-6">\n          <Link href="/about" className="text-sm font-medium transition-colors hover:text-primary">About</Link>\n        </nav>\n      </div>\n    </header>\n  )\n}\n'''
        with open(self.base_path / "src/components/shared/header.tsx", "w", encoding="utf-8") as f: f.write(header_component)
        print("🧩 Tạo sample components")

    def create_sample_hooks(self):
        """Tạo các custom hooks mẫu"""
        use_debounce = '''import { useState, useEffect } from 'react'\n\nexport function useDebounce<T>(value: T, delay: number): T {\n  const [debouncedValue, setDebouncedValue] = useState<T>(value)\n\n  useEffect(() => {\n    const handler = setTimeout(() => {\n      setDebouncedValue(value)\n    }, delay)\n\n    return () => {\n      clearTimeout(handler)\n    }\n  }, [value, delay])\n\n  return debouncedValue\n}\n'''
        with open(self.base_path / "src/hooks/useDebounce.ts", "w", encoding="utf-8") as f: f.write(use_debounce)
        print("🎣 Tạo custom hooks")

    def create_sample_context(self):
        """Tạo sample context"""
        theme_context = '''"use client"\n\nimport { createContext, useContext, useEffect, useState, ReactNode } from 'react'\n\ntype Theme = 'dark' | 'light' | 'system'\n\ninterface ThemeProviderState {\n  theme: Theme\n  setTheme: (theme: Theme) => void\n}\n\nconst ThemeProviderContext = createContext<ThemeProviderState | undefined>(undefined)\n\nexport function ThemeProvider({ children, defaultTheme = 'system', storageKey = 'vite-ui-theme' }: { children: ReactNode, defaultTheme?: Theme, storageKey?: string }) {\n  const [theme, setTheme] = useState<Theme>(\n    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme\n  )\n\n  useEffect(() => {\n    const root = window.document.documentElement\n    root.classList.remove('light', 'dark')\n    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'\n    root.classList.add(theme === 'system' ? systemTheme : theme)\n  }, [theme])\n\n  const value = {\n    theme,\n    setTheme: (theme: Theme) => {\n      localStorage.setItem(storageKey, theme)\n      setTheme(theme)\n    },\n  }\n\n  return (\n    <ThemeProviderContext.Provider value={value}>\n      {children}\n    </ThemeProviderContext.Provider>\n  )\n}\n\nexport const useTheme = () => {\n  const context = useContext(ThemeProviderContext)\n  if (context === undefined) throw new Error('useTheme must be used within a ThemeProvider')\n  return context\n}\n'''
        with open(self.base_path / "src/contexts/ThemeContext.tsx", "w", encoding="utf-8") as f: f.write(theme_context)
        print("🌍 Tạo sample context")

    def create_api_examples(self):
        """Tạo API examples"""
        api_route = '''import { NextRequest, NextResponse } from 'next/server'\n\nexport async function GET(request: NextRequest) {\n  return NextResponse.json({ message: 'Hello from API' })\n}\n'''
        with open(self.base_path / "src/app/api/example/route.ts", "w", encoding="utf-8") as f: f.write(api_route)
        print("🔗 Tạo API examples")

    # ===================================================================
    # 7. File phụ trợ
    # ===================================================================

    def create_env_files(self):
        """Tạo environment files"""
        env_example = '''# API URL\nNEXT_PUBLIC_API_URL=http://localhost:8000/api\n\n# App Info\nNEXT_PUBLIC_APP_NAME=My Next.js App\n'''
        with open(self.base_path / ".env.example", "w", encoding="utf-8") as f: f.write(env_example)
        with open(self.base_path / ".env.local", "w", encoding="utf-8") as f: f.write("# Local development variables\n")
        print("🌍 Tạo environment files")

    def create_gitignore(self):
        """Tạo .gitignore"""
        gitignore_content = '''# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.\n\n# dependencies\n/node_modules\n\n# next.js\n/.next/\n/out/\n\n# local env files\n.env*.local\n\n# vercel\n.vercel\n\n# misc\n.DS_Store\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*\n'''
        with open(self.base_path / ".gitignore", "w", encoding="utf-8") as f: f.write(gitignore_content)
        
        dockerignore_content = '''Dockerfile*\ndocker-compose*.yml\n.dockerignore\n.git\n.gitignore\nnode_modules\n.env\n.env.*\n.next\nREADME.md\n'''
        with open(self.base_path / ".dockerignore", "w", encoding="utf-8") as f: f.write(dockerignore_content)
        print("🚫 Tạo .gitignore và .dockerignore")

    def create_readme(self):
        """Tạo README.md"""
        readme_content = f'# {self.project_name}\n\nThis is a Next.js project bootstrapped with a custom Python script.\n\n## Getting Started\n\nFirst, install the dependencies:\n```bash\nnpm install\n```\n\nThen, run the development server:\n```bash\nnpm run dev\n```\n\nOpen [http://localhost:3000](http://localhost:3000) with your browser to see the result.\n'
        with open(self.base_path / "README.md", "w", encoding="utf-8") as f: f.write(readme_content)
        print("📖 Tạo README.md")

    # ===================================================================
    # Hàm chính để chạy tất cả
    # ===================================================================
    def generate_template(self):
        """Tạo toàn bộ template"""
        print("=" * 50)
        self.create_directory_structure()
        self.create_package_json()
        self.create_typescript_config()
        self.create_nextjs_config()
        self.create_tailwind_config()
        self.create_postcss_config()
        self.create_eslint_config()
        self.create_prettier_config()
        self.create_vscode_settings()
        self.create_docker_files()
        self.create_app_files()
        self.create_css_files()
        self.create_lib_files()
        self.create_types_file()
        self.create_sample_components()
        self.create_sample_hooks()
        self.create_sample_context()
        self.create_api_examples()
        self.create_env_files()
        self.create_gitignore()
        self.create_readme()
        print("\n" + "=" * 50)
        print(f"✅ HOÀN THÀNH! Dự án '{self.project_name}' đã được tạo.")
        print(f"🚀 Các bước tiếp theo:\n  1. cd {self.project_name}\n  2. npm install\n  3. npm run dev")

def main():
    """Hàm main để chạy chương trình"""
    project_name = "my-nextjs-app"
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    
    if Path(project_name).exists():
        overwrite = input(f"⚠️ Thư mục '{project_name}' đã tồn tại. Ghi đè? (y/N): ").strip().lower()
        if overwrite in ['y', 'yes']:
            shutil.rmtree(project_name)
        else:
            print("❌ Hủy tạo dự án.")
            sys.exit(0)

    generator = NextJSTemplateGenerator(project_name)
    generator.generate_template()

if __name__ == "__main__":
    main()