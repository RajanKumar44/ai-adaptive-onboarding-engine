PROFICIENCY_LEVELS = {
    "beginner": {
        "description": "No prior experience or basic awareness",
        "hours_to_intermediate": 80,
    },
    "intermediate": {
        "description": "Can work independently on standard tasks",
        "hours_to_advanced": 120,
    },
    "advanced": {
        "description": "Deep expertise; can mentor others",
        "hours_to_expert": 200,
    },
    "expert": {
        "description": "Industry-recognized authority",
        "hours_to_expert": 0,
    },
}

SKILL_LEARNING_PATHS = {
    "react": {
        "beginner": [
            {
                "step": 1,
                "title": "JavaScript & ES6 Fundamentals",
                "description": "Master modern JavaScript before diving into React.",
                "resources": [
                    "https://javascript.info/",
                    "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 2,
                "title": "React Core Concepts",
                "description": "Learn components, props, state, and lifecycle.",
                "resources": [
                    "https://react.dev/learn",
                    "https://www.freecodecamp.org/learn/front-end-development-libraries/",
                ],
                "estimated_hours": 30,
            },
            {
                "step": 3,
                "title": "Hooks & Functional Components",
                "description": "Understand useState, useEffect, useContext, and custom hooks.",
                "resources": [
                    "https://react.dev/reference/react",
                    "https://usehooks.com/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 4,
                "title": "State Management",
                "description": "Learn Redux Toolkit or Zustand for global state.",
                "resources": [
                    "https://redux-toolkit.js.org/",
                    "https://zustand-demo.pmnd.rs/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 5,
                "title": "Build a Full Project",
                "description": "Create a real-world React application.",
                "resources": [
                    "https://github.com/topics/react-projects",
                ],
                "estimated_hours": 25,
            },
        ],
        "intermediate": [
            {
                "step": 1,
                "title": "Performance Optimization",
                "description": "useMemo, useCallback, React.memo, code-splitting.",
                "resources": [
                    "https://react.dev/learn/render-and-commit",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 2,
                "title": "Testing with React Testing Library",
                "description": "Write unit and integration tests for React components.",
                "resources": [
                    "https://testing-library.com/docs/react-testing-library/intro/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 3,
                "title": "Next.js for SSR/SSG",
                "description": "Server-side rendering and static site generation.",
                "resources": [
                    "https://nextjs.org/docs",
                ],
                "estimated_hours": 25,
            },
        ],
    },
    "python": {
        "beginner": [
            {
                "step": 1,
                "title": "Python Basics",
                "description": "Variables, data types, control flow, functions, and modules.",
                "resources": [
                    "https://docs.python.org/3/tutorial/",
                    "https://www.learnpython.org/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 2,
                "title": "Object-Oriented Programming",
                "description": "Classes, inheritance, encapsulation, and polymorphism.",
                "resources": [
                    "https://realpython.com/python3-object-oriented-programming/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 3,
                "title": "Standard Library & Packages",
                "description": "os, sys, pathlib, datetime, json, requests, and pip.",
                "resources": [
                    "https://docs.python.org/3/library/",
                    "https://pypi.org/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 4,
                "title": "Testing with pytest",
                "description": "Write reliable tests for your Python code.",
                "resources": [
                    "https://docs.pytest.org/en/stable/",
                ],
                "estimated_hours": 10,
            },
        ],
        "intermediate": [
            {
                "step": 1,
                "title": "Async Programming",
                "description": "asyncio, aiohttp, and async/await patterns.",
                "resources": [
                    "https://realpython.com/async-io-python/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 2,
                "title": "Advanced Python Patterns",
                "description": "Decorators, generators, context managers, metaclasses.",
                "resources": [
                    "https://realpython.com/primer-on-python-decorators/",
                ],
                "estimated_hours": 20,
            },
        ],
    },
    "postgresql": {
        "beginner": [
            {
                "step": 1,
                "title": "SQL Fundamentals",
                "description": "SELECT, INSERT, UPDATE, DELETE, and JOINs.",
                "resources": [
                    "https://www.postgresql.org/docs/current/tutorial.html",
                    "https://sqlzoo.net/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 2,
                "title": "Schema Design",
                "description": "Tables, indexes, constraints, and normalization.",
                "resources": [
                    "https://www.postgresql.org/docs/current/ddl.html",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 3,
                "title": "Advanced Queries",
                "description": "CTEs, window functions, subqueries, and aggregations.",
                "resources": [
                    "https://mode.com/sql-tutorial/",
                ],
                "estimated_hours": 20,
            },
        ],
        "intermediate": [
            {
                "step": 1,
                "title": "Performance Tuning",
                "description": "EXPLAIN ANALYZE, index strategies, query optimization.",
                "resources": [
                    "https://www.postgresql.org/docs/current/performance-tips.html",
                ],
                "estimated_hours": 20,
            },
        ],
    },
    "docker": {
        "beginner": [
            {
                "step": 1,
                "title": "Container Basics",
                "description": "Images, containers, volumes, and networks.",
                "resources": [
                    "https://docs.docker.com/get-started/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 2,
                "title": "Writing Dockerfiles",
                "description": "Best practices for building efficient images.",
                "resources": [
                    "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/",
                ],
                "estimated_hours": 10,
            },
            {
                "step": 3,
                "title": "Docker Compose",
                "description": "Define and run multi-container applications.",
                "resources": [
                    "https://docs.docker.com/compose/",
                ],
                "estimated_hours": 10,
            },
        ],
    },
    "kubernetes": {
        "beginner": [
            {
                "step": 1,
                "title": "Kubernetes Architecture",
                "description": "Nodes, pods, deployments, services, and namespaces.",
                "resources": [
                    "https://kubernetes.io/docs/concepts/",
                    "https://www.katacoda.com/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 2,
                "title": "kubectl & Manifests",
                "description": "Writing YAML manifests and managing resources.",
                "resources": [
                    "https://kubernetes.io/docs/reference/kubectl/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 3,
                "title": "Helm Charts",
                "description": "Package, configure, and deploy applications with Helm.",
                "resources": [
                    "https://helm.sh/docs/",
                ],
                "estimated_hours": 15,
            },
        ],
    },
    "aws": {
        "beginner": [
            {
                "step": 1,
                "title": "AWS Core Services",
                "description": "EC2, S3, IAM, VPC, and RDS fundamentals.",
                "resources": [
                    "https://aws.amazon.com/getting-started/",
                    "https://explore.skillbuilder.aws/",
                ],
                "estimated_hours": 25,
            },
            {
                "step": 2,
                "title": "Serverless with Lambda",
                "description": "Build event-driven functions without servers.",
                "resources": [
                    "https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 3,
                "title": "AWS CLI & CloudFormation",
                "description": "Automate infrastructure with code.",
                "resources": [
                    "https://docs.aws.amazon.com/cli/",
                    "https://docs.aws.amazon.com/cloudformation/",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 4,
                "title": "AWS Certification Prep",
                "description": "Prepare for AWS Solutions Architect - Associate.",
                "resources": [
                    "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                ],
                "estimated_hours": 40,
            },
        ],
        "intermediate": [
            {
                "step": 1,
                "title": "EKS & Container Services",
                "description": "Deploy containerized workloads on AWS.",
                "resources": [
                    "https://docs.aws.amazon.com/eks/",
                ],
                "estimated_hours": 20,
            },
        ],
    },
}
