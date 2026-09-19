import os
import sys
import logging
from app.crawler.models import CrawledDocument
from app.indexer.index_manager import index_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_data")

SAMPLE_DOCUMENTS = [
    {
        "url": "https://fastapi.tiangolo.com/tutorial/first-steps/",
        "domain": "fastapi.tiangolo.com",
        "title": "FastAPI - First Steps and Quickstart",
        "body_text": """
        FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.
        The key features are: Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic).
        Fast to code: Increase the speed to develop features by about 200% to 300%.
        Fewer bugs: Reduce about 40% of human induced errors. Intuitive: Great editor support. Completion everywhere.
        Less time debugging. Robust: Get production-ready code with automatic interactive documentation.
        Standards-based: Based on and fully compatible with the open standards for APIs: OpenAPI and JSON Schema.
        """
    },
    {
        "url": "https://www.sqlite.org/fts5.html",
        "domain": "sqlite.org",
        "title": "SQLite FTS5 Extension and BM25 Full-Text Search",
        "body_text": """
        FTS5 is an SQLite virtual table module that provides full-text search capability to database applications.
        Full-text search engines allow the user to search a collection of documents for occurrences of specified keywords or phrases.
        FTS5 supports prefix searches, phrase searches, boolean queries with AND, OR, NOT operators, and column-specific filters.
        FTS5 provides an auxiliary bm25() function that calculates a ranking score according to the Okapi BM25 algorithm.
        Lower values indicate better matches. Furthermore, FTS5 includes highlight() and snippet() helper functions
        to extract contextual text fragments with matched words wrapped in custom tags such as <mark>.
        """
    },
    {
        "url": "https://www.sbert.net/docs/pretrained_models.html",
        "domain": "sbert.net",
        "title": "Sentence-Transformers: all-MiniLM-L6-v2 Dense Embeddings",
        "body_text": """
        The sentence-transformers library provides state-of-the-art sentence, text and image embeddings.
        The all-MiniLM-L6-v2 model maps sentences and paragraphs to a 384 dimensional dense vector space.
        It was trained on over 1 billion sentence pairs from diverse datasets including Reddit, Wikipedia, StackExchange, and Yahoo Answers.
        It is optimized for speed, producing high quality embeddings with minimal computational footprint,
        making it ideal for lightweight CPU deployment and mobile/edge search applications.
        Vectors are compared using cosine similarity to perform semantic search and nearest neighbor retrieval.
        """
    },
    {
        "url": "https://en.wikipedia.org/wiki/Reciprocal_rank_fusion",
        "domain": "en.wikipedia.org",
        "title": "Reciprocal Rank Fusion (RRF) in Information Retrieval",
        "body_text": """
        Reciprocal Rank Fusion (RRF) is an algorithm that evaluates and merges multiple search result lists with different scoring systems.
        RRF takes the ranked lists produced by independent retrieval systems (such as lexical BM25 and dense vector cosine similarity),
        and assigns a score based on the reciprocal rank of each item in the individual lists.
        The formula is RRF(d) = sum(1 / (k + r(d))), where k is a smoothing constant typically set around 60.
        RRF has been shown to consistently outperform individual retrieval strategies and naive score normalization,
        providing high precision and robust hybrid search recall across heterogeneous document collections.
        """
    },
    {
        "url": "https://docs.trychroma.com/getting-started",
        "domain": "trychroma.com",
        "title": "ChromaDB - Open Source Vector Database",
        "body_text": """
        Chroma is the AI-native open-source embedding database designed to make it easy to build LLM and semantic search apps.
        Chroma gives you the tools to store embeddings and their metadata, embed documents and queries, and search embeddings.
        It runs in-memory, embedded directly inside Python applications, or as a client-server distributed system.
        Chroma uses HNSW (Hierarchical Navigable Small World) graph indexing to achieve fast approximate nearest neighbor (ANN) lookups
        across millions of dense vectors with cosine, L2, or inner product distance metrics.
        """
    },
    {
        "url": "https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/",
        "domain": "kubernetes.io",
        "title": "What is Kubernetes? Container Orchestration Platform",
        "body_text": """
        Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services,
        that facilitates both declarative configuration and automation. It has a large, rapidly growing ecosystem.
        Kubernetes provides service discovery, load balancing, storage orchestration, automated rollouts and rollbacks,
        automatic bin packing, self-healing containers, and secret and configuration management.
        Kubernetes clusters consist of control plane nodes and worker nodes running container runtimes like containerd or CRI-O.
        """
    },
    {
        "url": "https://redis.io/docs/about/",
        "domain": "redis.io",
        "title": "Redis: In-Memory Data Store, Cache, and Message Broker",
        "body_text": """
        Redis is an open source, in-memory data store used by millions of developers as a database, cache, streaming engine, and message broker.
        Redis provides data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs,
        geospatial indexes, and streams. Redis has built-in replication, Lua scripting, LRU eviction, transactions, and different levels of on-disk persistence.
        It delivers sub-millisecond response times enabling millions of operations per second for real-time applications.
        """
    },
    {
        "url": "https://www.postgresql.org/about/",
        "domain": "postgresql.org",
        "title": "PostgreSQL: The World's Most Advanced Open Source Relational Database",
        "body_text": """
        PostgreSQL is a powerful, open source object-relational database system with over 35 years of active development
        that has earned it a strong reputation for reliability, feature robustness, and performance.
        PostgreSQL comes with many features aimed at helping developers build applications, administrators to protect data integrity
        and build fault-tolerant environments, and manage data no matter how big or small the dataset.
        It natively supports ACID transactions, foreign keys, subqueries, triggers, user-defined types, functions, and JSONB document storage.
        """
    },
    {
        "url": "https://www.docker.com/resources/what-container/",
        "domain": "docker.com",
        "title": "What is a Container? Docker Virtualization Explained",
        "body_text": """
        A container is a standard unit of software that packages up code and all its dependencies so the application runs quickly
        and reliably from one computing environment to another. A Docker container image is a lightweight, standalone,
        executable package of software that includes everything needed to run an application: code, runtime, system tools,
        system libraries and settings. Container images become containers at runtime when they run on Docker Engine.
        Containers isolate software from its environment and ensure that it works uniformly despite differences between development and staging.
        """
    },
    {
        "url": "https://docs.python.org/3/library/asyncio.html",
        "domain": "docs.python.org",
        "title": "asyncio — Asynchronous I/O in Python Standard Library",
        "body_text": """
        asyncio is a library to write concurrent code using the async/await syntax.
        asyncio is used as a foundation for multiple Python asynchronous frameworks that provide high-performance network
        and web-servers, database connection libraries, distributed task queues, etc.
        asyncio is often a perfect fit for IO-bound and high-level structured network code.
        asyncio provides a set of high-level APIs to run Python coroutines concurrently and have full control over their execution,
        perform network IO and IPC, control subprocesses, distribute tasks via queues, and synchronize concurrent code.
        """
    },
    {
        "url": "https://graphql.org/learn/",
        "domain": "graphql.org",
        "title": "Introduction to GraphQL - A Query Language for your API",
        "body_text": """
        GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data.
        GraphQL provides a complete and understandable description of the data in your API, gives clients the power to ask for exactly
        what they need and nothing more, makes it easier to evolve APIs over time, and enables powerful developer tools.
        Unlike REST APIs which require loading from multiple URLs, GraphQL APIs get all the data your app needs in a single request.
        Apps using GraphQL are fast and stable because they control the data they get, not the server.
        """
    },
    {
        "url": "https://react.dev/learn",
        "domain": "react.dev",
        "title": "React: The Library for Web and Native User Interfaces",
        "body_text": """
        React lets you build user interfaces out of individual pieces called components.
        Create your own React components like Thumbnail, LikeButton, and Video. Then combine them into entire screens, pages, and apps.
        Whether you work on your own or with thousands of other developers, using React feels the same.
        It is designed to let you seamlessly combine components written by independent people, teams, and organizations.
        React hooks like useState, useEffect, useMemo, and useCallback provide ergonomic state management and side effect coordination.
        """
    },
    {
        "url": "https://vitejs.dev/guide/",
        "domain": "vitejs.dev",
        "title": "Vite: Next Generation Frontend Tooling",
        "body_text": """
        Vite is a modern frontend build tool that significantly improves the frontend development experience.
        It consists of two major parts: a dev server that provides rich feature enhancements over native ES modules,
        for example extremely fast Hot Module Replacement (HMR), and a build command that bundles your code with Rollup,
        pre-configured to output highly optimized static assets for production.
        Vite aims to address developer ergonomics by leveraging native browser ES modules and esbuild for lightning fast startup.
        """
    },
    {
        "url": "https://www.elastic.co/what-is/elasticsearch",
        "domain": "elastic.co",
        "title": "What is Elasticsearch? Distributed Search & Analytics Engine",
        "body_text": """
        Elasticsearch is a distributed, free and open search and analytics engine for all types of data, including textual,
        numerical, geospatial, structured, and unstructured. Elasticsearch is built on Apache Lucene and was first released in 2010.
        Known for its simple REST APIs, distributed nature, speed, and scalability, Elasticsearch is the central component of the Elastic Stack.
        It uses inverted indices for instantaneous full-text searches and supports dense vector fields for k-nearest neighbor (kNN) semantic search.
        """
    },
    {
        "url": "https://aws.amazon.com/s3/",
        "domain": "aws.amazon.com",
        "title": "Amazon S3: Cloud Object Storage Built to Retrieve Any Amount of Data",
        "body_text": """
        Amazon Simple Storage Service (Amazon S3) is an object storage service offering industry-leading scalability,
        data availability, security, and performance. Customers of all sizes and industries can store and protect any amount of data
        for virtually any use case, such as data lakes, cloud-native applications, and mobile apps.
        With cost-effective storage classes and easy-to-use management features, you can optimize costs, organize data,
        and configure fine-tuned access controls to meet specific business, organizational, and compliance requirements.
        """
    },
    {
        "url": "https://nginx.org/en/",
        "domain": "nginx.org",
        "title": "NGINX High Performance Web Server and Reverse Proxy",
        "body_text": """
        NGINX is a high-performance HTTP server, reverse proxy, and IMAP/POP3 proxy server.
        NGINX is known for its high performance, stability, rich feature set, simple configuration, and low resource consumption.
        Unlike traditional servers, NGINX doesn't rely on threads to handle requests. Instead, it uses a much more scalable
        event-driven (asynchronous) architecture. This architecture uses small, but more importantly, predictable amounts of memory under load.
        Even if you don't expect to handle thousands of simultaneous requests, you can still benefit from NGINX's high performance and small memory footprint.
        """
    },
    {
        "url": "https://kafka.apache.org/documentation/",
        "domain": "kafka.apache.org",
        "title": "Apache Kafka: Distributed Event Streaming Platform",
        "body_text": """
        Apache Kafka is an open-source distributed event streaming platform used by thousands of companies for high-performance
        data pipelines, streaming analytics, data integration, and mission-critical applications.
        Event streaming is the digital equivalent of the human body's central nervous system.
        It is the technological foundation for the 'always-on' world where businesses are increasingly software-defined and automated.
        Kafka combines storage, stream processing, and publish/subscribe messaging in a fault-tolerant, horizontally scalable architecture.
        """
    },
    {
        "url": "https://huggingface.co/docs/transformers/index",
        "domain": "huggingface.co",
        "title": "Hugging Face Transformers: State-of-the-Art Machine Learning",
        "body_text": """
        Transformers provides thousands of pretrained models to perform tasks on different modalities such as text, vision, and audio.
        With Transformers, you can easily download and train state-of-the-art pretrained models for text classification,
        information extraction, question answering, summarization, translation, text generation, and dense vector feature extraction.
        Transformers supports interoperability between PyTorch, TensorFlow, and JAX frameworks.
        """
    },
    {
        "url": "https://prometheus.io/docs/introduction/overview/",
        "domain": "prometheus.io",
        "title": "Prometheus Monitoring System and Time Series Database",
        "body_text": """
        Prometheus is an open-source systems monitoring and alerting toolkit originally built at SoundCloud.
        Prometheus joins the Cloud Native Computing Foundation as the second hosted project, after Kubernetes.
        Prometheus collects and stores its metrics as time series data, i.e. metrics information is stored with the timestamp
        at which it was recorded, alongside optional key-value pairs called labels.
        Prometheus features a multi-dimensional data model, a flexible query language called PromQL, and autonomous single server nodes.
        """
    },
    {
        "url": "https://grpc.io/docs/what-is-grpc/introduction/",
        "domain": "grpc.io",
        "title": "gRPC: Modern Open Source High Performance Remote Procedure Call",
        "body_text": """
        gRPC is a modern open source high performance Remote Procedure Call (RPC) framework that can run in any environment.
        It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication.
        By default, gRPC uses Protocol Buffers, Google’s mature open source mechanism for serializing structured data.
        In gRPC, a client application can directly call a method on a server application on a different machine as if it were a local object,
        making it easier for you to create distributed applications and services.
        """
    },
    {
        "url": "https://git-scm.com/doc",
        "domain": "git-scm.com",
        "title": "Git Distributed Version Control System",
        "body_text": """
        Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency.
        Git is easy to learn and has a tiny footprint with lightning fast performance.
        It outclasses SCM tools like Subversion, CVS, Perforce, and ClearCase with features like cheap local branching,
        convenient staging areas, and multiple workflows.
        Every Git directory on every computer is a full-fledged repository with complete history and full version-tracking capabilities.
        """
    },
    {
        "url": "https://www.linux.org/pages/what-is-linux/",
        "domain": "linux.org",
        "title": "Linux Operating System Kernel and Open Source Architecture",
        "body_text": """
        Linux is a family of open-source Unix-like operating systems based on the Linux kernel, an operating system kernel
        first released on September 17, 1991, by Linus Torvalds. Linux is typically packaged in a Linux distribution.
        Distributions include the Linux kernel and supporting system software and libraries, many of which are provided by the GNU Project.
        Popular Linux distributions include Debian, Ubuntu, Fedora, CentOS, Arch Linux, and Alpine Linux for tiny container base images.
        """
    },
    {
        "url": "https://onnxruntime.ai/docs/",
        "domain": "onnxruntime.ai",
        "title": "ONNX Runtime: Cross-Platform High Performance ML Inferencing Engine",
        "body_text": """
        ONNX Runtime is a cross-platform, high performance scoring engine for Open Neural Network Exchange (ONNX) models.
        ONNX Runtime enables you to apply hardware optimizations across different platforms and hardware (CPUs, GPUs, and NPUs).
        ONNX Runtime provides APIs for Python, C++, C#, Java, and JavaScript.
        It enables lightweight, sub-second inference execution with quantized INT8 and FP16 weights,
        cutting memory consumption and latency in microservice and edge container environments.
        """
    }
]

def seed_database():
    logger.info(f"Seeding search engine with {len(SAMPLE_DOCUMENTS)} documents...")
    total_chunks = 0
    for idx, doc_data in enumerate(SAMPLE_DOCUMENTS, start=1):
        doc = CrawledDocument(
            id=f"seed_doc_{idx}",
            url=doc_data["url"],
            domain=doc_data["domain"],
            title=doc_data["title"],
            body_text=doc_data["body_text"],
            raw_html_length=len(doc_data["body_text"])
        )
        chunks = index_manager.ingest_document(doc)
        total_chunks += len(chunks)
        logger.info(f"[{idx}/{len(SAMPLE_DOCUMENTS)}] Indexed '{doc.title}' ({len(chunks)} chunks)")

    logger.info(f"Seeding completed successfully! Total documents: {len(SAMPLE_DOCUMENTS)}, Total chunks: {total_chunks}")

if __name__ == "__main__":
    seed_database()
