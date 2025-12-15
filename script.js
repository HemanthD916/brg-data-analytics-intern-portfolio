// Main JavaScript for the Data Analytics Intern Portfolio

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId.startsWith('#')) {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Active navigation link highlighting
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('nav a');
    
    function highlightNavLink() {
        let scrollPosition = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    // Add active class styling
    const style = document.createElement('style');
    style.textContent = `
        nav a.active {
            background-color: rgba(255, 255, 255, 0.25) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
    `;
    document.head.appendChild(style);
    
    window.addEventListener('scroll', highlightNavLink);
    highlightNavLink(); // Initial call

    // Project filtering functionality
    const filterButtons = document.createElement('div');
    filterButtons.className = 'project-filters';
    filterButtons.innerHTML = `
        <button class="filter-btn active" data-filter="all">All Projects</button>
        <button class="filter-btn" data-filter="python">Python</button>
        <button class="filter-btn" data-filter="sql">SQL</button>
        <button class="filter-btn" data-filter="r">R</button>
        <button class="filter-btn" data-filter="cpp">C++</button>
    `;
    
    const projectsSection = document.getElementById('projects');
    if (projectsSection) {
        projectsSection.insertBefore(filterButtons, projectsSection.children[1]);
        
        // Add filter styles
        const filterStyle = document.createElement('style');
        filterStyle.textContent = `
            .project-filters {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0 30px;
            }
            .filter-btn {
                padding: 10px 20px;
                background: #f0f7ff;
                border: 2px solid #2a5298;
                border-radius: 30px;
                color: #2a5298;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .filter-btn:hover,
            .filter-btn.active {
                background: #2a5298;
                color: white;
                transform: translateY(-2px);
            }
        `;
        document.head.appendChild(filterStyle);
        
        // Filter projects based on button click
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                const projects = document.querySelectorAll('.project');
                
                projects.forEach(project => {
                    if (filter === 'all') {
                        project.style.display = 'block';
                    } else {
                        const projectTech = project.getAttribute('data-tech') || '';
                        if (projectTech.includes(filter)) {
                            project.style.display = 'block';
                        } else {
                            project.style.display = 'none';
                        }
                    }
                });
            });
        });
        
        // Add data-tech attributes to projects
        const projects = document.querySelectorAll('.project');
        projects.forEach((project, index) => {
            if (index === 0) project.setAttribute('data-tech', 'python');
            else if (index === 1) project.setAttribute('data-tech', 'sql');
            else if (index === 2) project.setAttribute('data-tech', 'r');
            else if (index === 3) project.setAttribute('data-tech', 'cpp');
        });
    }

    // Add copy code functionality
    document.querySelectorAll('pre').forEach(codeBlock => {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-code-btn';
        copyButton.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: #007acc;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
            transition: background 0.3s ease;
        `;
        
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyButton);
        
        copyButton.addEventListener('click', function() {
            const code = codeBlock.querySelector('code')?.textContent || codeBlock.textContent;
            navigator.clipboard.writeText(code).then(() => {
                const originalText = copyButton.textContent;
                copyButton.textContent = 'Copied!';
                copyButton.style.background = '#4CAF50';
                
                setTimeout(() => {
                    copyButton.textContent = originalText;
                    copyButton.style.background = '#007acc';
                }, 2000);
            });
        });
    });

    // Dynamic year in footer
    const currentYear = new Date().getFullYear();
    const yearSpan = document.querySelector('footer p');
    if (yearSpan && yearSpan.textContent.includes('2025')) {
        yearSpan.textContent = yearSpan.textContent.replace('2025', currentYear);
    }

    // Add scroll-to-top button
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '↑';
    scrollTopBtn.className = 'scroll-top-btn';
    scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: #2a5298;
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 1.5rem;
        cursor: pointer;
        display: none;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(scrollTopBtn);
    
    scrollTopBtn.addEventListener('mouseenter', () => {
        scrollTopBtn.style.transform = 'scale(1.1)';
        scrollTopBtn.style.background = '#1e3c72';
    });
    
    scrollTopBtn.addEventListener('mouseleave', () => {
        scrollTopBtn.style.transform = 'scale(1)';
        scrollTopBtn.style.background = '#2a5298';
    });
    
    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollTopBtn.style.display = 'block';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });

    // Add typing animation for header
    const headerText = "Hemanth Dhamodharan";
    const headerElement = document.querySelector('header h1');
    if (headerElement) {
        headerElement.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < headerText.length) {
                headerElement.textContent += headerText.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        
    // Start typing animation after a short delay
    setTimeout(typeWriter, 500);
    }

    // Initialize Analytics tracking (if you add analytics later)
    function initAnalytics() {
        console.log('Portfolio analytics initialized');
        // You can add Google Analytics or other tracking here
    }

    initAnalytics();
});
