export default function Footer() {
  return (
    <footer className="bg-white border-t mt-12">
      <div className="max-w-7xl mx-auto px-6 py-6 text-center text-gray-600">
        <p>
          © {new Date().getFullYear()} Smart Route Planner. All rights reserved.
        </p>
        <div className="mt-2 flex justify-center gap-6">
          <a href="https://github.com/248Vansh/TheCords" className="hover:text-blue-600">GitHub</a>
          <a href="#privacy" className="hover:text-blue-600">Privacy</a>
          <a href="#contact" className="hover:text-blue-600">Contact</a>
        </div>
      </div>
    </footer>
  );
}
