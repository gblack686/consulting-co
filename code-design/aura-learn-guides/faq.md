# FAQ

Source: https://www.aura.build/learn/faq
Scraped: 2026-03-05

---

Frequently Asked Questions

Answers to every question collected from our product, pricing, and template pages—organized in one place so you can move faster.

Aura basics

Core questions about how Aura works, which models it supports, and how you can get started.

How does Aura work?

Aura is a web-based AI design assistant. You can generate HTML, CSS, and JavaScript designs using text prompts, reference templates and components with @, edit visually in Design Mode, and publish or export your creations. All processing happens in your browser and the cloud.

Can I generate designs with Aura?

Yes. Aura includes design generation so you can create visual content using text prompts. Pro and Max plans unlock design mode and export options.

Does Aura work offline?

No. Aura is a web-based application that requires an internet connection to access AI models and generate content. All processing happens in the cloud for the best performance and latest model access.

Which AI models does Aura support?

Aura integrates GPT-5.1, GPT-5, Claude Opus 4.5, Claude Sonnet 4.5, Gemini 3 Pro, and Gemini 2.5 Pro. Pro and Max plans unlock premium models like Claude Opus 4.5, Claude Sonnet 4.5, and Gemini 3 Pro for higher-quality results.

What apps can Aura integrate with?

Aura can export designs to Figma using the browser console method, and you can import designs from Figma by pasting Figma URLs. You can also export full sites as HTML/CSS/JS files to continue development in any code editor or deploy to hosting platforms like Netlify or Vercel.

What are the system requirements for Aura?

Aura is a web application that works in any modern browser. You'll need a stable internet connection and a modern web browser like Chrome, Firefox, Safari, or Edge. No downloads or installations required—just visit aura.build and start creating.

Can I try Aura before purchasing?

Yes. The Free plan includes 10 monthly messages that work with all AI models, so you can test core features before upgrading.

Pricing & billing

Plan details, limits, and billing controls drawn from the Pricing and core FAQ content.

What pricing plans does Aura offer?

Free gives 10 monthly messages. Pro, Max, and Ultra increase monthly message limits (120, 240, and 560 respectively), unlock premium models, design mode, exports, and priority access.

How do message limits work?

All AI models (GPT, Claude, Gemini) count toward the same usage limit. Free gets 10 monthly messages, Pro gets 120 (including 20 bonus), Max gets 240 (including 40 bonus), and Ultra gets 560 (including 60 bonus). You can use any available model within your plan's message allowance.

Is there a free trial for Pro or Max plans?

There’s no timed trial, but the Free plan lets you use every model with a small monthly allowance so you can evaluate before upgrading.

Can I upgrade or downgrade my plan?

Yes. Upgrades apply immediately; downgrades take effect at the next billing cycle.

Do unused messages roll over to the next month?

No. Message allowances reset each billing cycle for all plans.

What payment methods do you accept?

Major credit cards and Apple Pay via Stripe are supported for subscriptions.

Features & workflow

Everything about templates, the editor, and how Aura differs from other tools.

How do I use @ to reference templates and components?

Use @ in prompts to pull in templates, components, or snippets—up to ~100,000 characters of context. Shift-click to reference multiple items at once.

Can I create multi-page websites with Aura?

Yes. Build as many pages as you need, link elements for navigation, add page transitions, and keep shared components consistent across the site.

How do I use this template?

Free or Pro templates can be remixed with the “Use for Free” or “Use as Pro” button. Paid templates require using the author’s “Buy” link to get access.

Can I customize this template?

Yes. After remixing or purchasing, you can change colors, fonts, images, layout, and content, or edit the code directly with prompts.

Do I need Pro to use this template?

Premium templates require a Pro subscription. Paid templates require purchasing from the author regardless of your plan.

Can I remix or share my version?

Yes. You can remix templates to create your own version and share your remixes with the community; credit stays with you.

Why do elements vanish in Design/Code view?

Heavy animations can hide elements. Remove or simplify them, or use the built-in Animate Keyframe/Animate on Scroll snippets optimized for the editor.

What's different from Lovable?

Aura focuses on Tailwind-based design output: real HTML/CSS/JS, 1,700+ templates, 1,400+ components, multi-page sites, and visual editing. Lovable is more full-stack app–oriented.

What's different from Framer, Webflow, or Figma Sites?

Aura outputs standard HTML, Tailwind CSS, and vanilla JS—no proprietary runtime. You can export, self-host, or keep editing in any code editor or Figma.

Am I tied to Aura when I design and publish?

No, it's just HTML and you can convert to Figma using our tool, Framer using their plugin and other popular platforms that use HTML.

Can you import fonts that aren't inside of Aura?

Yes, you can just mention the font name in the prompt. Or you can do so in the code. As long as it's an online font like Google Fonts, or a URL it'll work.

My project is resource-intensive and the screen freezes when I try to make changes. What should I do?

If your page is freezing when trying to make changes, go to Home and click on "Iterations" next to Chat. Hover over the iteration and click on Delete. Before deleting, please copy your code as a backup to avoid any data loss. To optimize your project without editing code, create multiple pages—each new page duplicates the original, which you can then adapt by asking the AI to remove specific sections or unused code. You can also request the AI to remove or adjust animations for improved performance. This approach helps reduce file size and prevent freezing without requiring direct code edits.

Why doesn't Aura remember my previous page selections when I switch to a new page?

Currently, Aura only processes the page you are actively viewing in the editor and does not retain context from previous pages or maintain a full build history. This is intentional to keep performance optimal and avoid overloading the system with too much context. However, when working on a single page, Aura will read up to several thousand lines of that page's HTML to assist you. If you need to reference previously completed sections, it's best to copy any necessary details into the current page's context or provide a summary prompt as you work. We're working on improving context handling in future updates, and your feedback helps prioritize these enhancements.

How do I design each page separately in Aura and combine them?

You can prompt and design each page separately in Aura. To connect the pages, use the "Link" feature—right-click an element and choose "Copy," then go to the target page and use "Paste to Replace" as needed. This helps transfer sections or navigation elements across pages. If this workflow doesn't meet your needs, you can download the HTML file from Aura and import it into Cursor. From there, you can prompt Cursor to rebuild or refine the structure as a complete project.

I'm trying to add custom logos to the landing page I'm building but I can't figure out how to upload my own assets.

Currently, direct SVG uploads aren't supported yet. You can, however, copy the SVG code from your file and include it directly in your prompt—even multiple SVGs at once. Alternatively, you could upload your SVG files to an external hosting platform (or FTP server) and reference the public URL in your prompt.

Publishing & export

How to publish, export, host, and connect forms or domains for your projects.

Can I export this template?

Yes. After remixing and customizing, you can export as HTML or send to Figma. Export options are available in the editor.

Can I export my site designs out of Aura?

Yes. Export full sites as HTML/CSS/JS, publish to subdomains, or export to Figma. All output is standard code you can continue anywhere.

How do I add my own domain?

Export your site, deploy to Netlify or Vercel, then configure your custom domain and DNS in their dashboards.

How do I build multiple pages?

Create pages in the Pages popover, link elements to pages, and manage navigation. Duplicating a page doesn’t auto-create new ones—you add them explicitly.

Where should I host my landing page?

Export HTML and drag-and-drop to Netlify or Vercel. Both have quick, low-setup hosting with free plans.

Where do form submissions go?

Forms are empty by default. Connect actions to Netlify Forms, Formspree, Getform, or Google Forms (a few lines of JS) to store submissions.

What happens to Unicorn Studio animations if servers go down?

Animated Unicorn Studio assets are hosted on Unicorn Studio by default. If you'd prefer to self-host the assets for more control or reliability, you can follow their official guide: https://www.unicorn.studio/docs/faqs/

Still need help?

Reach out and we’ll get back quickly.

Contact support
Aura basics
Pricing & billing
Features & workflow
Publishing & export
PRODUCT
Create
Templates
Components
Assets
Pricing
Changelog
Affiliates
WHAT WE USE
Mobbin
Screen Studio
Courses
UI Kit
Video Editor
Mockups
CONNECT
Privacy
Terms
Support
Report Issue
LinkedIn
X

© 2026 Aura. All rights reserved. Made with Cursor.
