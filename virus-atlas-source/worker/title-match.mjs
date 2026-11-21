// Match explicit virus aliases in titles, preserving letter/number boundaries.
// Database phrase matching alone can collapse the "A" in "hepatitis A".
export function titleMatches(title, aliases) {
  const normalize = value => String(value || '').toLowerCase().replace(/[–—‐]/g, '-');
  const text = normalize(title);
  if (/reverse.genetic|gain.of.function|host.range|pseudotyp|viral.entry|receptor.bind|mutagen|engineer|vector.construct|optimized.*protein|protein.*optimiz|replicon|infectious.clone|recombinant.*construct|virus.rescue|molecular.clon|cell.entry/i.test(text)) return false;
  return (aliases || []).some(alias => {
    const words = normalize(alias).trim().split(/\s+/);
    if (!words.length || !words[0]) return false;
    const escaped = words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s+');
    return new RegExp('(?:^|[^a-z0-9])' + escaped + '(?:es|s)?(?=$|[^a-z0-9])', 'i').test(text);
  });
}
