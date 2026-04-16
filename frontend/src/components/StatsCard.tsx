interface StatsCardProps {
  value: string | number;
  label: string;
  color: "blue" | "green" | "yellow" | "pink";
}

const COLOR_MAP = {
  blue: "bg-blue-50 text-blue-800",
  green: "bg-green-50 text-green-800",
  yellow: "bg-amber-50 text-amber-800",
  pink: "bg-pink-50 text-pink-800",
};

export default function StatsCard({ value, label, color }: StatsCardProps) {
  return (
    <div className={`rounded-lg p-4 text-center ${COLOR_MAP[color]}`}>
      <div className="text-3xl font-bold">{value}</div>
      <div className="mt-1 text-xs text-gray-500">{label}</div>
    </div>
  );
}
