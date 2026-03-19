SKILL_KEYWORDS = {
    # Programming Languages
    "python": ["python", "py"],
    "javascript": ["javascript", "js", "node.js", "nodejs"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "jvm"],
    "kotlin": ["kotlin"],
    "swift": ["swift", "ios"],
    "go": ["golang"],
    "rust": ["rust"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", "dotnet", ".net"],
    "php": ["php"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "scala": ["scala"],
    "r": ["r programming", "rlang"],
    "dart": ["dart"],
    "elixir": ["elixir"],
    "haskell": ["haskell"],
    "clojure": ["clojure"],
    "perl": ["perl"],
    "lua": ["lua"],
    "bash": ["bash", "shell scripting", "bash scripting"],
    "powershell": ["powershell"],

    # Frontend Frameworks & Libraries
    "react": ["react", "react.js", "reactjs", "react native"],
    "angular": ["angular", "angularjs", "angular.js"],
    "vue": ["vue", "vue.js", "vuejs"],
    "svelte": ["svelte"],
    "nextjs": ["next.js", "nextjs"],
    "nuxtjs": ["nuxt.js", "nuxtjs"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss", "less", "tailwind", "tailwindcss", "bootstrap"],
    "jquery": ["jquery"],
    "redux": ["redux", "redux toolkit", "mobx"],
    "graphql": ["graphql"],
    "webpack": ["webpack", "vite", "parcel"],

    # Backend Frameworks
    "fastapi": ["fastapi"],
    "django": ["django", "django rest framework", "drf"],
    "flask": ["flask"],
    "express": ["express", "express.js"],
    "spring": ["spring", "spring boot", "spring framework"],
    "laravel": ["laravel"],
    "nestjs": ["nestjs", "nest.js"],
    "gin": ["gin", "gin-gonic"],
    "actix": ["actix", "actix-web"],
    "rails": ["rails"],

    # Databases
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "sqlite": ["sqlite"],
    "elasticsearch": ["elasticsearch", "elastic"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb"],
    "oracle": ["oracle", "oracle db"],
    "mssql": ["mssql", "sql server", "microsoft sql"],
    "neo4j": ["neo4j", "graph database"],
    "influxdb": ["influxdb"],

    # Cloud Platforms
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation", "eks", "ecs"],
    "azure": ["azure", "microsoft azure", "az"],
    "gcp": ["gcp", "google cloud", "google cloud platform", "gke"],
    "cloudflare": ["cloudflare"],
    "digitalocean": ["digitalocean"],
    "heroku": ["heroku"],
    "vercel": ["vercel"],
    "netlify": ["netlify"],

    # DevOps & Infrastructure
    "docker": ["docker", "dockerfile", "docker-compose"],
    "kubernetes": ["kubernetes", "k8s", "kubectl", "helm"],
    "terraform": ["terraform", "iac"],
    "ansible": ["ansible"],
    "jenkins": ["jenkins"],
    "github actions": ["github actions", "ci/cd", "cicd"],
    "gitlab ci": ["gitlab ci", "gitlab-ci"],
    "circleci": ["circleci"],
    "prometheus": ["prometheus"],
    "grafana": ["grafana"],
    "nginx": ["nginx"],
    "apache": ["apache"],
    "linux": ["linux", "ubuntu", "centos", "debian"],

    # Data & ML
    "machine learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "deep learning": ["deep learning", "dl", "neural networks", "cnn", "rnn", "lstm"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "spark": ["apache spark", "pyspark", "spark"],
    "hadoop": ["hadoop", "hdfs", "mapreduce"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt", "data build tool"],
    "mlflow": ["mlflow"],
    "nlp": ["nlp", "natural language processing", "bert", "gpt", "transformers"],
    "computer vision": ["computer vision", "cv", "opencv"],

    # APIs & Protocols
    "rest": ["rest", "restful", "rest api"],
    "grpc": ["grpc"],
    "websocket": ["websocket", "ws"],
    "oauth": ["oauth", "oauth2", "jwt", "authentication"],

    # Testing
    "pytest": ["pytest"],
    "jest": ["jest"],
    "selenium": ["selenium"],
    "cypress": ["cypress"],
    "unittest": ["unittest", "unit testing", "integration testing"],

    # Version Control
    "git": ["git", "github", "gitlab", "bitbucket"],

    # Methodologies
    "agile": ["agile", "scrum", "kanban", "sprint"],
    "microservices": ["microservices", "micro-services"],
    "solid": ["solid principles", "design patterns"],
}

SKILL_CATEGORIES = {
    "languages": [
        "python", "javascript", "typescript", "java", "kotlin", "swift", "go",
        "rust", "c++", "c#", "php", "ruby", "scala", "r", "dart", "elixir",
        "haskell", "clojure", "perl", "lua", "bash", "powershell",
    ],
    "frontend": [
        "react", "angular", "vue", "svelte", "nextjs", "nuxtjs", "html", "css",
        "jquery", "redux", "graphql", "webpack",
    ],
    "backend": [
        "fastapi", "django", "flask", "express", "spring", "laravel", "nestjs",
        "gin", "actix", "rails",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch",
        "cassandra", "dynamodb", "oracle", "mssql", "neo4j", "influxdb",
    ],
    "cloud": ["aws", "azure", "gcp", "cloudflare", "digitalocean", "heroku", "vercel", "netlify"],
    "devops": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "circleci", "prometheus", "grafana",
        "nginx", "apache", "linux",
    ],
    "data_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "pandas", "numpy", "spark", "hadoop", "kafka",
        "airflow", "dbt", "mlflow", "nlp", "computer vision",
    ],
    "other": [
        "rest", "grpc", "websocket", "oauth", "pytest", "jest", "selenium",
        "cypress", "unittest", "git", "agile", "microservices", "solid",
    ],
}
