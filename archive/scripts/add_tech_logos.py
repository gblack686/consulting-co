import re

# Read the HTML file
with open('technology-logos.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract just the first set of icons (before DUPLICATE SET)
first_set_match = re.search(r'<!-- First Set of Icons -->(.*?)<!-- DUPLICATE SET', html_content, re.DOTALL)
if first_set_match:
    first_set = first_set_match.group(1)
else:
    print("Could not find first set of icons")
    exit(1)

# Convert HTML class to className for JSX
jsx_content = first_set.replace('class=', 'className=')

# Create the TechMarquee component
component = '''export default function TechMarquee() {
  return (
    <section className="py-16 overflow-hidden border-b border-[#D6D4C8]/60 bg-[#E6E4D9]/30 relative z-10">
      <div className="w-full relative">
        {/* Left Fade */}
        <div className="absolute left-0 top-0 bottom-0 w-32 z-20 bg-gradient-to-r from-[#E6E4D9]/50 via-[#E6E4D9]/50 to-transparent"></div>
        {/* Right Fade */}
        <div className="absolute right-0 top-0 bottom-0 w-32 z-20 bg-gradient-to-l from-[#E6E4D9]/50 via-[#E6E4D9]/50 to-transparent"></div>

        {/* Marquee Track */}
        <div className="animate-marquee flex gap-16 items-center pl-16">
          {/* First Set of Icons */}
          <div className="flex gap-16 items-center">
''' + jsx_content + '''
          </div>

          {/* Duplicate Set for Seamless Loop */}
          <div className="flex gap-16 items-center" aria-hidden="true">
''' + jsx_content + '''
          </div>
        </div>
      </div>
    </section>
  );
}
'''

# Write the component
with open('gb-automation-landing/src/components/TechMarquee.jsx', 'w', encoding='utf-8') as f:
    f.write(component)

print("TechMarquee.jsx updated successfully!")
print("Run: cd gb-automation-landing && git add . && git commit -m 'Update tech logos' && git push")
