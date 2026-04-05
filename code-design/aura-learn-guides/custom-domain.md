# Custom Domain

Source: https://www.aura.build/learn/custom-domain
Scraped: 2026-03-05

---

How to Set Up a Custom Domain

Connect your own domain to your Aura projects for a professional, branded experience. Your visitors will see your custom domain instead of the default Aura subdomain.

Custom Domain Support

By default, your published Aura projects are hosted on an Aura subdomain (e.g., yourproject.aura.build). With a PRO subscription, you can connect your own custom domain to give your projects a more professional appearance.

HOW IT WORKS

When you connect a custom domain, visitors to your domain (e.g., yourdomain.com) will see your Aura project while the URL stays on your domain. This is perfect for portfolios, landing pages, and client projects.

Requirements

Before connecting a custom domain, make sure you have the following:

PRO subscription — Custom domains are a PRO feature

A published project — Your project must be published first

A domain you own — Purchased from a domain registrar (e.g., Name.com, Namecheap, GoDaddy, Cloudflare)

Access to DNS settings — You'll need to add DNS records at your domain registrar

Purchase a Domain

To connect a custom domain to your Aura project, you first need to purchase a domain from a domain registrar.

1

Choose a Domain Registrar — Purchase a domain from a provider such as Name.com, Cloudflare, Namecheap, GoDaddy, or Porkbun. Prices typically range from $10-15/year for common extensions like .com.

2

Register Your Domain — Search for your desired domain name and complete the purchase. Make sure you have access to the DNS management panel.

Popular Domain Registrars

Most registrars have DNS management panels under "Domain Settings" or "DNS Records". Here are guides for adding A Records and CNAMEs:

Name.com
Namecheap
GoDaddy
Cloudflare
IONOS
Porkbun
Connect Your Domain

Follow these steps to connect your custom domain to your Aura project:

1

Open your project in the Aura editor and click the Publish button in the top navigation bar to open the Publish popover.

2

In the Publish popover, click Custom Domain (next to the URL label) to reveal the custom domain settings.

3

Enter your domain name in the input field. You can use either an apex domain (e.g., yourdomain.com) or a subdomain (e.g., blog.yourdomain.com). Aura will check if the domain is available.

4

Click Save Domain to save your custom domain. Aura will automatically configure SSL certificates for your domain.

Important

You must publish your project first before you can add a custom domain. The Custom Domain option is only available for published projects.

DNS Configuration

After saving your domain in Aura, you need to configure your DNS settings at your domain registrar. The configuration depends on whether you're using an apex domain or a subdomain.

Option 1: Apex Domain (e.g., yourdomain.com)

For apex domains (also called "root" or "naked" domains), you need to add two DNS records:

Type	Name	Value
A	@	75.2.60.5
CNAME	www	aura.build
A Record (@)

Points your apex domain (e.g., yourdomain.com) to Aura's servers.

CNAME Record (www)

Points your www subdomain (e.g., www.yourdomain.com) to Aura.

Option 2: Subdomain (e.g., blog.yourdomain.com)

For subdomains (like blog.yourdomain.com, app.yourdomain.com, or shop.yourdomain.com), you only need one CNAME record:

Type	Name	Value
CNAME	blog (your subdomain)	aura.build
Why subdomains are simpler

Subdomains only require a single CNAME record, making them easier to configure. They also don't affect your main domain's DNS records, which is useful if you're already using your apex domain for email or another website.

TIP

For apex domains, ensure there are no other A or AAAA records configured, as they may interfere with Aura's settings.

Verification

After configuring your DNS records, it may take some time for the changes to propagate. Here's what to expect:

DNS Propagation

DNS changes can take up to 48 hours to propagate worldwide, though it's usually much faster.

Automatic SSL

Aura automatically provisions SSL certificates. Your site will be accessible via HTTPS once DNS is configured.

You can check propagation status using tools like dnschecker.org

Troubleshooting

Having issues connecting your domain? Here are some common problems and solutions:

Domain shows "SSL Error" or "Not Secure"

This usually means DNS hasn't fully propagated yet. Wait a few hours and try again. SSL certificates are provisioned automatically once DNS is correctly configured.

Domain shows wrong content or homepage

Make sure:

•
Your DNS records are correctly configured (A record pointing to 75.2.60.5)
•
The domain is saved correctly in the Publish popover
•
There are no conflicting A or AAAA records for your domain
"Domain already in use" error

Each domain can only be connected to one Aura project. If you see this error, the domain may already be connected to another project. Remove it from the other project first, or use a subdomain instead.

Can't add CNAME for apex domain (@)

CNAME records cannot be used on apex domains (the "naked" domain without www). This is a DNS specification limitation. Use the A record (75.2.60.5) for your apex domain and CNAME for the www subdomain.

Subdomain not working

If your subdomain (like blog.yourdomain.com) isn't working:

•
Verify the CNAME record points to aura.build
•
Make sure you entered the exact subdomain in Aura (e.g., blog.yourdomain.com, not just yourdomain.com)
•
Subdomains don't need an A record — only a CNAME
Requirements
Purchase a Domain
Connect Your Domain
DNS Configuration
Verification
Troubleshooting
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
