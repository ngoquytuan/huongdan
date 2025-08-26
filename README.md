Tôi sẽ tạo một chương trình Python để tạo template cấu trúc thư mục Next.js với Docker:

```python
#!/usr/bin/env python3
"""
Next.js Template Generator with Docker
Tạo cấu trúc thư mục chuẩn cho dự án Next.js với TypeScript và Docker
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class NextJSTemplateGenerator:
    def __init__(self, project_name: str = "my-nextjs-template"):
        self.project_name = project_name
        self.base_path = Path(project_name)
    
    def create_directory_structure(self):
        """Tạo cấu trúc thư mục"""
        directories = [
            # VS Code settings
            ".vscode",
            
            # Public assets
            "public/icons",
            "public/images",
            
            # Source code structure
            "src/app/(main)",
            "src/app/api",
            "src/components/shared",
            "src/components/ui",
            "src/contexts",
            "src/hooks",
            "src/lib",
            "src/types",
        ]
        
        print(f"🚀 Tạo dự án Next.js: {self.project_name}")
        
        # Tạo thư mục gốc
        self.base_path.mkdir(exist_ok=True)
        
        # Tạo các thư mục con
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Tạo thư mục: {directory}")
        
        # Tạo file .gitkeep cho các thư mục trống
        gitkeep_dirs = [
            "public/icons",
            "public/images",
            "src/app/api",
            "src/components/shared",
            "src/components/ui",
            "src/contexts",
            "src/hooks",
        ]
        
        for directory in gitkeep_dirs:
            gitkeep_file = self.base_path / directory / ".gitkeep"
            gitkeep_file.touch()
    
    def create_package_json(self):
        """Tạo package.json với dependencies cần thiết"""
        package_json = {
            "name": self.project_name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "lint:fix": "next lint --fix",
                "type-check": "tsc --noEmit",
                "docker:dev": "docker-compose up --build",
                "docker:prod": "docker-compose -f docker-compose.prod.yml up --build"
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "axios": "^1.6.0",
                "clsx": "^2.0.0",
                "lucide-react": "^0.294.0",
                "tailwind-merge": "^2.0.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "autoprefixer": "^10.0.0",
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0",
                "postcss": "^8.0.0",
                "prettier": "^3.0.0",
                "tailwindcss": "^3.0.0",
                "typescript": "^5.0.0"
            }
        }
        
        with open(self.base_path / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
        print("📦 Tạo package.json")
    
    def create_typescript_config(self):
        """Tạo tsconfig.json"""
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [
                    {
                        "name": "next"
                    }
                ],
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
        print("⚙️ Tạo tsconfig.json")
    
    def create_nextjs_config(self):
        """Tạo next.config.mjs"""
        config_content = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  // Cấu hình cho Docker
  output: 'standalone',
}

export default nextConfig
'''
        
        with open(self.base_path / "next.config.mjs", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("⚙️ Tạo next.config.mjs")
    
    def create_tailwind_config(self):
        """Tạo tailwind.config.ts"""
        config_content = '''import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}

export default config
'''
        
        with open(self.base_path / "tailwind.config.ts", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("🎨 Tạo tailwind.config.ts")
    
    def create_eslint_config(self):
        """Tạo .eslintrc.json"""
        eslint_config = {
            "extends": [
                "next/core-web-vitals",
                "@typescript-eslint/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "plugins": ["@typescript-eslint"],
            "rules": {
                "@typescript-eslint/no-unused-vars": "error",
                "@typescript-eslint/no-explicit-any": "warn",
                "prefer-const": "error"
            }
        }
        
        with open(self.base_path / ".eslintrc.json", "w", encoding="utf-8") as f:
            json.dump(eslint_config, f, indent=2)
        print("🔍 Tạo .eslintrc.json")
    
    def create_prettier_config(self):
        """Tạo .prettierrc"""
        prettier_config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False
        }
        
        with open(self.base_path / ".prettierrc", "w", encoding="utf-8") as f:
            json.dump(prettier_config, f, indent=2)
        print("💅 Tạo .prettierrc")
    
    def create_vscode_settings(self):
        """Tạo VS Code settings"""
        settings = {
            "typescript.preferences.importModuleSpecifier": "relative",
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": "explicit"
            },
            "files.associations": {
                "*.css": "tailwindcss"
            }
        }
        
        with open(self.base_path / ".vscode/settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        print("🔧 Tạo VS Code settings")
    
    def create_docker_files(self):
        """Tạo Dockerfile và docker-compose.yml"""
        
        # Dockerfile
        dockerfile_content = '''FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \\
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \\
  elif [ -f package-lock.json ]; then npm ci; \\
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \\
  else echo "Lockfile not found." && exit 1; \\
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
'''
        
        with open(self.base_path / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml (development)
        docker_compose_content = '''version: '3.8'

services:
  nextjs-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: base
    container_name: nextjs-dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NODE_ENV=development
    command: npm run dev
    restart: unless-stopped

networks:
  default:
    name: nextjs-network
'''
        
        with open(self.base_path / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(docker_compose_content)
        
        # docker-compose.prod.yml (production)
        docker_compose_prod_content = '''version: '3.8'

services:
  nextjs-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nextjs-prod
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped

networks:
  default:
    name: nextjs-network
'''
        
        with open(self.base_path / "docker-compose.prod.yml", "w", encoding="utf-8") as f:
            f.write(docker_compose_prod_content)
        
        print("🐳 Tạo Docker files")
    
    def create_app_files(self):
        """Tạo các file chính của Next.js App"""
        
        # Root layout
        root_layout = '''import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'My Next.js App',
  description: 'Generated by Next.js Template Generator',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
'''
        
        with open(self.base_path / "src/app/layout.tsx", "w", encoding="utf-8") as f:
            f.write(root_layout)
        
        # Main layout
        main_layout = '''import { ReactNode } from 'react'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">My Next.js App</h1>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="border-t mt-auto">
        <div className="container mx-auto px-4 py-4 text-center text-sm text-gray-600">
          © 2024 My Next.js App. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
'''
        
        with open(self.base_path / "src/app/(main)/layout.tsx", "w", encoding="utf-8") as f:
            f.write(main_layout)
        
        # Home page
        home_page = '''export default function HomePage() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Welcome to Next.js
        </h1>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          Your Next.js application is ready! Start building amazing things.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-semibold mb-2">Documentation</h3>
          <p className="text-gray-600">Find in-depth information about Next.js features and API.</p>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-semibold mb-2">Learn</h3>
          <p className="text-gray-600">Learn about Next.js in an interactive course with quizzes!</p>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h3 className="text-xl font-semibold mb-2">Deploy</h3>
          <p className="text-gray-600">Instantly deploy your Next.js site to a public URL with Vercel.</p>
        </div>
      </div>
    </div>
  )
}
'''
        
        with open(self.base_path / "src/app/(main)/page.tsx", "w", encoding="utf-8") as f:
            f.write(home_page)
        
        print("📄 Tạo App files")
    
    def create_lib_files(self):
        """Tạo các file trong thư mục lib"""
        
        # API client
        api_client = '''import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
'''
        
        with open(self.base_path / "src/lib/api.ts", "w", encoding="utf-8") as f:
            f.write(api_client)
        
        # Utils
        utils_content = '''import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}
'''
        
        with open(self.base_path / "src/lib/utils.ts", "w", encoding="utf-8") as f:
            f.write(utils_content)
        
        print("📚 Tạo lib files")
    
    def create_types_file(self):
        """Tạo file types"""
        types_content = '''// Common types used across the application

export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  createdAt: string
  updatedAt: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}
'''
        
        with open(self.base_path / "src/types/index.d.ts", "w", encoding="utf-8") as f:
            f.write(types_content)
        
        print("🔤 Tạo types file")
    
    def create_css_files(self):
        """Tạo CSS files"""
        globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
'''
        
        with open(self.base_path / "src/app/globals.css", "w", encoding="utf-8") as f:
            f.write(globals_css)
        
        print("🎨 Tạo CSS files")
    
    def create_env_files(self):
        """Tạo environment files"""
        env_example = '''# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database

# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Auth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# External Services
NEXT_PUBLIC_APP_NAME=My Next.js App
NEXT_PUBLIC_APP_VERSION=1.0.0
'''
        
        with open(self.base_path / ".env.example", "w", encoding="utf-8") as f:
            f.write(env_example)
        
        env_local = '''# Local development environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=development-secret-key-change-in-production
'''
        
        with open(self.base_path / ".env.local", "w", encoding="utf-8") as f:
            f.write(env_local)
        
        print("🌍 Tạo environment files")
    
    def create_gitignore(self):
        """Tạo .gitignore"""
        gitignore_content = '''# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js
.yarn/install-state.gz

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts

# Docker
Dockerfile.dockerignore
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
'''
        
        with open(self.base_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        
        # .dockerignore
        dockerignore_content = '''Dockerfile*
docker-compose*.yml
.dockerignore
.git
.gitignore
README.md
.env
.env.*
.nyc_output
coverage
.vscode
.idea
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
'''
        
        with open(self.base_path / ".dockerignore", "w", encoding="utf-8") as f:
            f.write(dockerignore_content)
        
        print("🚫 Tạo .gitignore và .dockerignore")
    
    def create_readme(self):
        """Tạo README.md"""
        readme_content = f'''# {self.project_name}

Next.js project được tạo với TypeScript, Tailwind CSS, và Docker support.

## 🚀 Bắt đầu

### Prerequisites

- Node.js 18+
- Docker & Docker Compose (optional)
- npm hoặc yarn

### Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd {self.project_name}
```

2. Cài đặt dependencies:
```bash
npm install
# hoặc
yarn install
```

3. Tạo file environment:
```bash
cp .env.example .env.local
```

4. Chạy development server:
```bash
npm run dev
# hoặc
yarn dev
```

Mở [http://localhost:3000](http://localhost:3000) để xem kết quả.

## 🐳 Docker

### Development với Docker

```bash
npm run docker:dev
```

### Production với Docker

```bash
npm run docker:prod
```

## 📁 Cấu trúc thư mục

```
{self.project_name}/
├── .vscode/               # VS Code settings
├── public/                # Static assets
│   ├── icons/
│   └── images/
└── src/                   # Source code
    ├── app/               # Next.js App Router
    │   ├── (main)/        # Route group
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   ├── api/           # API routes
    │   └── layout.tsx     # Root layout
    ├── components/        # React components
    │   ├── shared/        # Custom components
    │   └── ui/            # UI library components
    ├── contexts/          # React contexts
    ├── hooks/             # Custom hooks
    ├── lib/               # Utilities
    │   ├── api.ts         # API client
    │   └── utils.ts       # Utility functions
    └── types/             # TypeScript types
        └── index.d.ts
```

## 🛠️ Scripts

- `npm run dev` - Chạy development server
- `npm run build` - Build production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run type-check` - Check TypeScript types
- `npm run docker:dev` - Run với Docker (development)
- `npm run docker:prod` - Run với Docker (production)

## 🧰 Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Linting:** ESLint + Prettier
- **Containerization:** Docker

## 📝 Environment Variables

Xem file `.env.example` để biết các biến môi trường cần thiết.

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add some amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.
'''
        
        with open(self.base_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("📖 Tạo README.md")
    
    def generate_template(self):
        """Tạo toàn bộ template"""
        print("=" * 50)
        print("  NEXT.JS TEMPLATE GENERATOR")
        print("=" * 50)
        
        self.create_directory_structure()
