"""
Skill knowledge base containing learning paths and resources.
Maps each skill to structured learning information.
"""

SKILL_KNOWLEDGE_BASE = {
    "python": {
        "beginner": [
            "Learn Python syntax and basic data types",
            "Understand variables, operators, and expressions",
            "Master control flow (if/else, loops)",
            "Learn functions and scope",
        ],
        "intermediate": [
            "Object-oriented programming (classes, inheritance)",
            "File I/O and error handling",
            "Working with libraries and modules",
            "Data structures (lists, dicts, sets, tuples)",
        ],
        "advanced": [
            "Design patterns in Python",
            "Decorators and context managers",
            "Async programming with asyncio",
            "Performance optimization and profiling",
        ],
        "resources": {
            "beginner": [
                {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "documentation"},
                {"title": "Codecademy Python Course", "url": "https://codecademy.com", "type": "course"},
            ],
            "intermediate": [
                {"title": "Real Python", "url": "https://realpython.com", "type": "tutorial"},
                {"title": "Python Design Patterns", "url": "https://refactoring.guru", "type": "documentation"},
            ],
            "advanced": [
                {"title": "Fluent Python Book", "url": "https://oreilly.com", "type": "book"},
                {"title": "Python Async IO", "url": "https://realpython.com/async-io-python/", "type": "tutorial"},
            ],
        },
        "estimated_hours": {
            "beginner": 40,
            "intermediate": 60,
            "advanced": 80,
        }
    },
    "fastapi": {
        "beginner": [
            "Understand FastAPI basics and routing",
            "Learn request and response models (Pydantic)",
            "Path parameters, query parameters, and request bodies",
            "Built-in validation and error handling",
        ],
        "intermediate": [
            "Dependency injection system",
            "Security and authentication (JWT, OAuth2)",
            "WebSockets for real-time communication",
            "Middleware and exception handlers",
        ],
        "advanced": [
            "Advanced middleware patterns",
            "Background tasks and events",
            "OpenAPI and auto-documentation",
            "Testing and debugging FastAPI applications",
        ],
        "resources": {
            "beginner": [
                {"title": "FastAPI Official Documentation", "url": "https://fastapi.tiangolo.com/", "type": "documentation"},
                {"title": "FastAPI Tutorial", "url": "https://realpython.com/fastapi-best-practices/", "type": "tutorial"},
            ],
            "intermediate": [
                {"title": "FastAPI Advanced Usage", "url": "https://fastapi.tiangolo.com/advanced/", "type": "documentation"},
                {"title": "Real Python FastAPI", "url": "https://realpython.com", "type": "course"},
            ],
            "advanced": [
                {"title": "FastAPI Performance Tuning", "url": "https://fastapi.tiangolo.com/deployment/", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 30,
            "intermediate": 50,
            "advanced": 70,
        }
    },
    "react": {
        "beginner": [
            "JSX syntax and concepts",
            "Components (functional and class-based)",
            "Props and state management",
            "Event handling and forms",
        ],
        "intermediate": [
            "Hooks (useState, useEffect, useContext)",
            "Component composition patterns",
            "State management libraries (Redux, Zustand)",
            "API integration and fetch",
        ],
        "advanced": [
            "Performance optimization (memoization, lazy loading)",
            "Advanced hooks and custom hooks",
            "Testing React components",
            "Server-side rendering (Next.js)",
        ],
        "resources": {
            "beginner": [
                {"title": "React Official Documentation", "url": "https://react.dev", "type": "documentation"},
                {"title": "React Tutorial", "url": "https://scrimba.com/learn/learnreact", "type": "course"},
            ],
            "intermediate": [
                {"title": "Advanced React Patterns", "url": "https://epicreact.dev", "type": "course"},
                {"title": "Redux Official Documentation", "url": "https://redux.js.org", "type": "documentation"},
            ],
            "advanced": [
                {"title": "Next.js Documentation", "url": "https://nextjs.org/docs", "type": "documentation"},
                {"title": "React Performance", "url": "https://kent.do/blog/react-performance", "type": "tutorial"},
            ],
        },
        "estimated_hours": {
            "beginner": 50,
            "intermediate": 80,
            "advanced": 100,
        }
    },
    "javascript": {
        "beginner": [
            "Variables, data types, and operators",
            "Control flow and loops",
            "Functions and scope",
            "DOM manipulation basics",
        ],
        "intermediate": [
            "Object-oriented JavaScript (prototypes, classes)",
            "Asynchronous JavaScript (callbacks, promises)",
            "Array and object methods",
            "Error handling and debugging",
        ],
        "advanced": [
            "Async/await and generators",
            "Module systems (CommonJS, ES modules)",
            "Design patterns and best practices",
            "Event handling and event bubbling",
        ],
        "resources": {
            "beginner": [
                {"title": "JavaScript.info", "url": "https://javascript.info", "type": "tutorial"},
                {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "type": "documentation"},
            ],
            "intermediate": [
                {"title": "Eloquent JavaScript", "url": "https://eloquentjavascript.net", "type": "book"},
                {"title": "You Don't Know JS", "url": "https://github.com/getify/You-Dont-Know-JS", "type": "book"},
            ],
            "advanced": [
                {"title": "JavaScript Design Patterns", "url": "https://refactoring.guru", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 40,
            "intermediate": 60,
            "advanced": 80,
        }
    },
    "sql": {
        "beginner": [
            "SQL basics: SELECT, INSERT, UPDATE, DELETE",
            "Database design and schema creation",
            "WHERE clauses and filtering",
            "Basic joins and relationships",
        ],
        "intermediate": [
            "Complex joins (INNER, LEFT, RIGHT, FULL)",
            "Aggregation and grouping",
            "Subqueries and CTEs",
            "Indexes and query optimization",
        ],
        "advanced": [
            "Window functions and analytics",
            "Transaction management and ACID properties",
            "Database administration and performance tuning",
            "Advanced optimization techniques",
        ],
        "resources": {
            "beginner": [
                {"title": "W3Schools SQL Tutorial", "url": "https://w3schools.com/sql/", "type": "tutorial"},
                {"title": "SQLZoo", "url": "https://sqlzoo.net", "type": "interactive"},
            ],
            "intermediate": [
                {"title": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "tutorial"},
                {"title": "LeetCode Database", "url": "https://leetcode.com/problems/database/", "type": "practice"},
            ],
            "advanced": [
                {"title": "SQL Performance Explained", "url": "https://sql-performance-explained.com", "type": "book"},
                {"title": "PostgreSQL Documentation", "url": "https://postgresql.org/docs", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 30,
            "intermediate": 50,
            "advanced": 70,
        }
    },
    "docker": {
        "beginner": [
            "Docker basics and concepts",
            "Images and containers",
            "Dockerfile syntax and commands",
            "Building and running containers",
        ],
        "intermediate": [
            "Docker Compose and multi-container applications",
            "Volume and network management",
            "Container optimization and best practices",
            "Registry and image management",
        ],
        "advanced": [
            "Kubernetes orchestration",
            "Advanced networking and storage",
            "Security and vulnerability scanning",
            "Docker in production environments",
        ],
        "resources": {
            "beginner": [
                {"title": "Docker Official Documentation", "url": "https://docs.docker.com", "type": "documentation"},
                {"title": "Docker for Beginners", "url": "https://play.docker.com", "type": "interactive"},
            ],
            "intermediate": [
                {"title": "Docker Compose Documentation", "url": "https://docs.docker.com/compose/", "type": "documentation"},
            ],
            "advanced": [
                {"title": "Kubernetes Documentation", "url": "https://kubernetes.io/docs", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 25,
            "intermediate": 45,
            "advanced": 65,
        }
    },
    "git": {
        "beginner": [
            "Git basics: init, add, commit, push",
            "Branches and switching between branches",
            "Clone and merge operations",
            "Understanding the staging area",
        ],
        "intermediate": [
            "Advanced branching strategies",
            "Rebasing and squashing commits",
            "Pull requests and code reviews",
            "Conflict resolution",
        ],
        "advanced": [
            "Advanced git internals",
            "Custom workflows and hooks",
            "Git aliases and customization",
            "Git in large teams",
        ],
        "resources": {
            "beginner": [
                {"title": "Pro Git Book", "url": "https://git-scm.com/book/en/v2", "type": "book"},
                {"title": "Atlassian Git Tutorial", "url": "https://atlassian.com/git/tutorials", "type": "tutorial"},
            ],
            "intermediate": [
                {"title": "GitHub Learning Lab", "url": "https://github.com/skills", "type": "interactive"},
            ],
            "advanced": [
                {"title": "Git Internals", "url": "https://git-scm.com/book/en/v2/Git-Internals", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 10,
            "intermediate": 20,
            "advanced": 30,
        }
    },
    "aws": {
        "beginner": [
            "AWS basics and core services",
            "EC2 instances and management",
            "S3 storage and bucket operations",
            "IAM roles and permissions",
        ],
        "intermediate": [
            "Networking: VPC, subnets, security groups",
            "RDS and database management",
            "Lambda and serverless computing",
            "CloudWatch and monitoring",
        ],
        "advanced": [
            "Auto-scaling and load balancing",
            "Infrastructure as Code (CloudFormation, Terraform)",
            "Advanced security practices",
            "Multi-region and disaster recovery",
        ],
        "resources": {
            "beginner": [
                {"title": "AWS Official Documentation", "url": "https://aws.amazon.com/documentation/", "type": "documentation"},
                {"title": "A Cloud Guru", "url": "https://acloudguru.com", "type": "course"},
            ],
            "intermediate": [
                {"title": "AWS Well-Architected Framework", "url": "https://aws.amazon.com/architecture/well-architected/", "type": "documentation"},
            ],
            "advanced": [
                {"title": "AWS Solutions Architecture", "url": "https://aws.amazon.com/solutions/", "type": "documentation"},
            ],
        },
        "estimated_hours": {
            "beginner": 50,
            "intermediate": 80,
            "advanced": 120,
        }
    },
    "typescript": {
        "beginner": [
            "TypeScript basics and type annotations",
            "Primitive types and type inference",
            "Interfaces and type aliases",
            "Basic generics",
        ],
        "intermediate": [
            "Advanced types: union, intersection, conditional types",
            "Modules and namespaces",
            "Decorators and metadata",
            "Class-based OOP patterns",
        ],
        "advanced": [
            "Advanced generics and utility types",
            "Type system internals",
            "Mapped types and conditional types",
            "Custom type guards and assertions",
        ],
        "resources": {
            "beginner": [
                {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/", "type": "documentation"},
                {"title": "TypeScript for Beginners", "url": "https://egghead.io", "type": "course"},
            ],
            "intermediate": [
                {"title": "TypeScript Advanced Types", "url": "https://www.typescriptlang.org/docs/handbook/advanced-types.html", "type": "documentation"},
            ],
            "advanced": [
                {"title": "TypeScript Deep Dive", "url": "https://basarat.gitbook.io/typescript/", "type": "book"},
            ],
        },
        "estimated_hours": {
            "beginner": 30,
            "intermediate": 50,
            "advanced": 70,
        }
    }
}


def get_skill_info(skill_name: str) -> dict:
    """
    Retrieve learning information for a specific skill.
    
    Args:
        skill_name: Name of the skill
        
    Returns:
        Dictionary with skill information or empty dict if not found
    """
    skill_lower = skill_name.lower().strip()
    return SKILL_KNOWLEDGE_BASE.get(skill_lower, {})


def get_all_skills() -> list:
    """
    Get list of all available skills in knowledge base.
    
    Returns:
        List of skill names
    """
    return list(SKILL_KNOWLEDGE_BASE.keys())
