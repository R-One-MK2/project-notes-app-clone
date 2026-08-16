import { Button } from "@/components/ui/button";
import React from "react";

export default function HomePage() {
  return (
    <div>
      <main>
        <h1 className="text-4xl font-bold">Notes App</h1>
        <p className="mt-4 text-gray-600">Your notes will live here</p>

        {/* div */}
        <div className="mt-8 flex">
          <Button>Primary Button</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="destructive">Destructive</Button>
        </div>
      </main>
    </div>
  );
}
