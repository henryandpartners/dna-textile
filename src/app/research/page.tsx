import Link from "next/link";
import Image from "next/image";
import fs from "fs";
import path from "path";

// Read data files at build time
function loadJson(filePath: string) {
  const fullPath = path.join(process.cwd(), filePath);
  return JSON.parse(fs.readFileSync(fullPath, "utf-8"));
}

interface Motif {
  type: string;
  [key: string]: unknown;
}

interface DiversityMetrics {
  mtDNA_h?: number;
  Y_STR_h?: number;
  [key: string]: string | number | undefined;
}

interface GeneticCommunity {
  language_family?: string;
  social_structure?: string;
  isolation_index?: number;
  diversity?: DiversityMetrics;
  notes?: string;
  [key: string]: string | number | DiversityMetrics | undefined;
}

interface CommunityData {
  name: string;
  motifs: Motif[];
  imageCount: number;
  geneticProfile?: GeneticCommunity;
}

export default function ResearchPage() {
  // Load genetics profiles
  const geneticProfile = loadJson("data/genetic_profile.json");
  const populationRels = loadJson("data/population_relationships.json");

  // Load all motif data
  const motifDir = path.join(process.cwd(), "motif_library");
  const motifFiles = fs.readdirSync(motifDir).filter((f) => f.endsWith(".json"));

  const communities: CommunityData[] = [];
  for (const file of motifFiles) {
    const motifData = loadJson(`motif_library/${file}`);
    const tribeName = motifData.community || file.replace("_motifs.json", "");
    const refDir = path.join(process.cwd(), "reference_images", tribeName);
    let imageCount = 0;
    if (fs.existsSync(refDir)) {
      imageCount = fs
        .readdirSync(refDir)
        .filter((f) => /\.(jpg|jpeg|png|webp)$/i.test(f)).length;
    }
    communities.push({
      name: tribeName,
      motifs: motifData.motifs || [],
      imageCount,
      geneticProfile: geneticProfile.communities[tribeName],
    });
  }

  // Compute totals
  const totalMotifs = communities.reduce((sum, c) => sum + c.motifs.length, 0);
  const totalImages = communities.reduce((sum, c) => sum + c.imageCount, 0);

  // Motif type counts
  const typeCounts: Record<string, number> = {};
  for (const c of communities) {
    for (const m of c.motifs) {
      typeCounts[m.type] = (typeCounts[m.type] || 0) + 1;
    }
  }

  // Language family groups
  const families: Record<string, string[]> = {};
  for (const [tribe, data] of Object.entries(
    geneticProfile.communities as Record<string, GeneticCommunity>
  )) {
    const fam = (data.language_family as string) || "Unknown";
    if (!families[fam]) families[fam] = [];
    families[fam].push(tribe);
  }

  // Fst matrix
  const fstMatrix: Record<string, Record<string, number>> = ((populationRels as Record<string, unknown>).distance_matrix as Record<string, Record<string, number>>) || {};

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
            <span className="text-2xl">🧬</span>
            <h1 className="text-lg font-bold">DNA Textile</h1>
          </Link>
          <Link
            href="/"
            className="text-sm text-gray-400 hover:text-gray-200 transition px-4 py-2 rounded-lg border border-gray-700 hover:border-gray-500"
          >
            ← Back to Generator
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 space-y-16">
        {/* Hero */}
        <section className="text-center">
          <div className="text-5xl mb-6">🧬🧵</div>
          <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            The Science Behind DNA Textile
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Where population genetics meets indigenous textile art — mapping{" "}
            <strong className="text-gray-200">{communities.length} Southeast Asian communities</strong>{" "}
            through their DNA and weaving traditions
          </p>
        </section>

        {/* Data Summary */}
        <section className="bg-gray-900 rounded-2xl border border-gray-800 p-8">
          <h3 className="text-xl font-bold mb-6">📊 Data Overview</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-800 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-blue-400">{communities.length}</div>
              <div className="text-sm text-gray-400 mt-1">Communities</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-purple-400">{totalMotifs}</div>
              <div className="text-sm text-gray-400 mt-1">Total Motifs</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-amber-400">{totalImages}</div>
              <div className="text-sm text-gray-400 mt-1">Reference Images</div>
            </div>
            <div className="bg-gray-800 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-green-400">
                {Object.keys(typeCounts).length}
              </div>
              <div className="text-sm text-gray-400 mt-1">Motif Types</div>
            </div>
          </div>

          {/* Motif type breakdown */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(typeCounts).map(([type, count]) => (
              <div key={type} className="bg-gray-800 rounded-lg p-3 text-center">
                <span className="text-2xl">
                  {type === "spiritual"
                    ? "🔮"
                    : type === "geometric"
                    ? "📐"
                    : type === "plant"
                    ? "🌿"
                    : type === "animal"
                    ? "🐾"
                    : "❓"}
                </span>
                <div className="text-lg font-bold mt-1">{count}</div>
                <div className="text-xs text-gray-500 capitalize">{type}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Research Foundation */}
        <section className="bg-gray-900 rounded-2xl border border-gray-800 p-8">
          <h3 className="text-xl font-bold mb-4">📚 Research Foundation</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-blue-300 mb-2">
                Dr. Metawee Srikummool
              </h4>
              <p className="text-gray-400 text-sm">
                Department of Biochemistry, Naresuan University, Thailand
              </p>
              <div className="mt-4 space-y-1 text-sm text-gray-300">
                <p>📊 62 published papers</p>
                <p>📈 1,753 citations</p>
                <p>🎯 h-index: 15</p>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                Key Publications
              </h4>
              {(geneticProfile.publications as string[]).map((pub, i) => (
                <div key={i} className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-sm text-gray-300">
                  {pub}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Social Structure → Genetic Signature */}
        <section>
          <h3 className="text-2xl font-bold mb-6">🔬 Key Finding: Social Structure → Genetic Signature</h3>
          <p className="text-gray-400 mb-8 max-w-4xl leading-relaxed">
            Postmarital residence patterns create predictable genetic signatures. How a community organizes marriage leaves a measurable imprint on DNA.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            {["matrilocal", "patrilocal", "nomadic"].map((structure) => {
              const matching = communities.filter(
                (c) => c.geneticProfile?.social_structure === structure
              );
              const colorConfig = {
                matrilocal: { bg: "bg-green-950/30", border: "border-green-800/50", text: "text-green-300", badge: "bg-green-900/50" },
                patrilocal: { bg: "bg-orange-950/30", border: "border-orange-800/50", text: "text-orange-300", badge: "bg-orange-900/50" },
                nomadic: { bg: "bg-red-950/30", border: "border-red-800/50", text: "text-red-300", badge: "bg-red-900/50" },
              } as const;
              const colors = colorConfig[structure as keyof typeof colorConfig];

              const avgIsolation =
                matching.reduce(
                  (s, c) => s + (Number(c.geneticProfile?.isolation_index) || 0),
                  0
                ) / (matching.length || 1);

              return (
                <div
                  key={structure}
                  className={`${colors.bg} ${colors.border} border rounded-xl p-6`}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-3xl">
                      {structure === "matrilocal" ? "♀️" : structure === "patrilocal" ? "♂️" : "⟳"}
                    </span>
                    <h4 className={`text-lg font-semibold ${colors.text} capitalize`}>
                      {structure}
                    </h4>
                  </div>
                  <p className="text-sm text-gray-300 mb-3">
                    {structure === "matrilocal"
                      ? "Women stay, men move in. ↑ Y diversity, ↓ mtDNA diversity."
                      : structure === "patrilocal"
                      ? "Men stay, women move in. ↑ mtDNA diversity, ↓ Y diversity."
                      : "Small, mobile groups. ↓ All markers — genetic drift."}
                  </p>
                  <div className={`${colors.badge} rounded-lg p-3 text-sm`}>
                    <p>Avg isolation: {avgIsolation.toFixed(2)}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {matching.length} communities:{" "}
                      {matching.map((c) => c.name).join(", ")}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Community Detail Cards */}
        <section>
          <h3 className="text-2xl font-bold mb-6">🗃️ Community Profiles</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {communities.map((community) => {
              const gp = community.geneticProfile;
              return (
                <div
                  key={community.name}
                  className="bg-gray-900 rounded-xl border border-gray-800 p-5 hover:border-gray-600 transition"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-lg font-bold">{community.name}</h4>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        community.imageCount > 0
                          ? "bg-green-900/50 text-green-300"
                          : "bg-red-900/50 text-red-300"
                      }`}
                    >
                      {community.imageCount} images
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-gray-400 mb-3">
                    {gp && (
                      <>
                        <p>
                          <span className="text-gray-300">Language:</span>{" "}
                          {gp.language_family}
                        </p>
                        <p>
                          <span className="text-gray-300">Social:</span>{" "}
                          <span className="capitalize">{gp.social_structure}</span>
                        </p>
                        <p>
                          <span className="text-gray-300">Isolation:</span>{" "}
                          {(gp.isolation_index ?? 0).toFixed(2)}
                        </p>
                        <p>
                          <span className="text-gray-300">Diversity:</span> mtDNA{" "}
                          {(gp.diversity?.mtDNA_h ?? 0).toFixed(2)} / Y-STR{" "}
                          {(gp.diversity?.Y_STR_h ?? 0).toFixed(2)}
                        </p>
                      </>
                    )}
                  </div>

                  <div className="text-xs text-gray-500 mb-3">
                    <span className="text-gray-400">{community.motifs.length} motifs</span>
                    {community.motifs.length > 0 && (
                      <>
                        {" "}
                        ·{" "}
                        {Object.entries(
                          community.motifs.reduce(
                            (acc: Record<string, number>, m) => {
                              acc[m.type] = (acc[m.type] || 0) + 1;
                              return acc;
                            },
                            {}
                          )
                        )
                          .map(([t, n]) => `${n} ${t}`)
                          .join(", ")}
                      </>
                    )}
                  </div>

                  {gp?.notes && (
                    <p className="text-xs text-gray-500 italic border-t border-gray-800 pt-3 mt-3">
                      {gp.notes}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* Genetic Distance Table */}
        <section>
          <h3 className="text-2xl font-bold mb-6">📏 Genetic Distance (Fst)</h3>
          <p className="text-gray-400 mb-6">
            Higher values = more genetic distance. 0 = identical, 1 = completely different.
          </p>
          <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-x-auto">
            <table className="text-xs w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="p-2 text-left text-gray-500 sticky left-0 bg-gray-900 z-10">
                    Tribe
                  </th>
                  {communities.map((c) => (
                    <th key={c.name} className="p-2 text-gray-500 min-w-[60px]">
                      {c.name.slice(0, 3)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {communities.map((row) => (
                  <tr key={row.name} className="border-b border-gray-800/50">
                    <td className="p-2 text-gray-300 font-medium sticky left-0 bg-gray-900 z-10">
                      {row.name}
                    </td>
                    {communities.map((col) => {
                      const val = fstMatrix?.[row.name]?.[col.name] ?? 0;
                      const color =
                        val < 0.05
                          ? "bg-green-900/40 text-green-300"
                          : val < 0.1
                          ? "bg-yellow-900/40 text-yellow-300"
                          : val < 0.15
                          ? "bg-orange-900/40 text-orange-300"
                          : "bg-red-900/40 text-red-300";
                      return (
                        <td key={col.name} className="p-2 text-center">
                          <span
                            className={`inline-block px-2 py-1 rounded ${color}`}
                          >
                            {val.toFixed(2)}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Visualizations */}
        <section>
          <h3 className="text-2xl font-bold mb-6">📈 Generated Visualizations</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { file: "01_genetic_diversity.png", title: "Genetic Diversity Radar" },
              { file: "02_mtDNA_haplogroups.png", title: "mtDNA Haplogroup Distribution" },
              { file: "03_Y_haplogroups.png", title: "Y-Chromosome Haplogroup Distribution" },
              { file: "04_genetic_distance.png", title: "Genetic Distance Heatmap" },
              { file: "05_cultural_isolation.png", title: "Cultural Isolation Index" },
              { file: "06_motif_dashboard.png", title: "Motif Library Dashboard" },
              { file: "07_social_genetic_signature.png", title: "Social Genetic Signature" },
            ].map((viz) => (
              <div key={viz.file} className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                <Image
                  src={`/research/${viz.file}`}
                  alt={viz.title}
                  width={800}
                  height={600}
                  className="w-full"
                />
                <div className="p-4">
                  <h4 className="text-sm font-semibold text-gray-300">{viz.title}</h4>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Language Family Map */}
        <section>
          <h3 className="text-2xl font-bold mb-6">🗂️ Language Families</h3>
          <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(families).map(([family, tribes]) => {
              const colors: Record<string, string> = {
                "Sino-Tibetan": "from-blue-900/50 to-blue-800/30 border-blue-700/50",
                "Hmong-Mien": "from-purple-900/50 to-purple-800/30 border-purple-700/50",
                Austroasiatic: "from-green-900/50 to-green-800/30 border-green-700/50",
                "Tai-Kadai": "from-orange-900/50 to-orange-800/30 border-orange-700/50",
                Austronesian: "from-pink-900/50 to-pink-800/30 border-pink-700/50",
              };
              const textColors: Record<string, string> = {
                "Sino-Tibetan": "text-blue-300",
                "Hmong-Mien": "text-purple-300",
                Austroasiatic: "text-green-300",
                "Tai-Kadai": "text-orange-300",
                Austronesian: "text-pink-300",
              };
              return (
                <div
                  key={family}
                  className={`bg-gradient-to-br ${colors[family] || "from-gray-800 to-gray-900"} border rounded-xl p-4`}
                >
                  <h4
                    className={`text-sm font-bold ${textColors[family] || "text-gray-300"} mb-2`}
                  >
                    {family}
                  </h4>
                  <div className="space-y-1">
                    {tribes.map((t) => (
                      <span
                        key={t}
                        className="block text-xs bg-gray-900/60 rounded px-2 py-0.5 text-gray-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-gray-800 pt-8 pb-16 text-center">
          <p className="text-xs text-gray-600 mb-4">
            Genetic data from Naresuan University research + published population genetics
            · Motif data from academic textile studies and ethnographic records
          </p>
          <Link
            href="/"
            className="inline-block text-sm text-blue-400 hover:text-blue-300 transition"
          >
            ← Back to Pattern Generator
          </Link>
        </footer>
      </main>
    </div>
  );
}
