// يصوّر promo.html إطار إطار ويحوله MP4 بمقاس 9:16 مع الموسيقى.
// الموسيقى: python3 music.py music.wav (تنبني مرة وحدة، وتنضاف تلقائياً)
// الاستخدام: node render.js --page promo.html --music music.wav --out promo.mp4
const { chromium } = require("playwright");
const { spawn, execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const arg = (k, d) => { const i = process.argv.indexOf("--" + k); return i > -1 ? process.argv[i + 1] : d; };
const pageFile = arg("page", "promo.html");
const base = pageFile.replace(/\.html$/, "");
const out = path.resolve(arg("out", path.join(__dirname, base + ".mp4")));
const fps = +arg("fps", 30);
const music = path.resolve(arg("music", path.join(__dirname, base === "promo" ? "music.wav" : base + ".wav")));
const ffmpeg = arg("ffmpeg", process.env.FFMPEG || execSync("python3 -c \"import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())\"").toString().trim());
const still = arg("still", null); // --still 5.5 يصوّر إطار واحد للمعاينة

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + path.join(__dirname, pageFile));
  await page.evaluate(() => document.fonts.ready);
  const qr = fs.readFileSync(path.join(__dirname, "qr.svg"), "utf8");
  await page.evaluate(s => { const q = document.getElementById("qrbox"); if (q) q.innerHTML = s; }, qr);
  console.log("fonts loaded:", await page.evaluate(() => document.fonts.check('700 40px "Readex Pro"')));

  if (still !== null) {
    for (const t of still.split(",")) {
      await page.evaluate(x => window.render(x), +t);
      await page.screenshot({ path: path.join(__dirname, `still-${base}-${t}.png`) });
    }
    await browser.close();
    return;
  }

  const frames = Math.round((await page.evaluate(() => window.DURATION)) * fps);
  const ff = spawn(ffmpeg, [
    "-y", "-f", "image2pipe", "-framerate", String(fps), "-i", "-",
    ...(fs.existsSync(music) ? ["-i", music] : ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]),
    "-shortest",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart",
    "-metadata", "title=فحص تسرّب العدّاد",
    out,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.render(t), i / fps);
    const buf = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (i % (fps * 5) === 0) console.log(`frame ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log("done:", out);
})();
