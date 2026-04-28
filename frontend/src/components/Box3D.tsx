import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import { Suspense } from "react";

interface Box3DProps {
  capacity: number;
  size: "small" | "medium" | "large";
}

function Room({ size }: { size: "small" | "medium" | "large" }) {
  const dims = {
    small: [4, 2.5, 3.5] as const,
    medium: [6, 3, 5] as const,
    large: [8, 3.2, 6.5] as const,
  }[size];
  const [w, h, d] = dims;

  return (
    <group>
      {/* Floor */}
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[w, d]} />
        <meshStandardMaterial color="#e8d9b8" />
      </mesh>
      {/* Back wall */}
      <mesh position={[0, h / 2, -d / 2]}>
        <boxGeometry args={[w, h, 0.1]} />
        <meshStandardMaterial color="#fde68a" />
      </mesh>
      {/* Left wall */}
      <mesh position={[-w / 2, h / 2, 0]}>
        <boxGeometry args={[0.1, h, d]} />
        <meshStandardMaterial color="#fcd34d" />
      </mesh>
      {/* Right wall (cut-away — half height) */}
      <mesh position={[w / 2, h / 4, 0]}>
        <boxGeometry args={[0.1, h / 2, d]} />
        <meshStandardMaterial color="#fcd34d" />
      </mesh>
      {/* Door */}
      <mesh position={[w / 2 - 0.4, 1, d / 2 - 0.05]} castShadow>
        <boxGeometry args={[0.9, 2, 0.1]} />
        <meshStandardMaterial color="#8B0000" />
      </mesh>
      {/* Table */}
      <mesh position={[0, 0.55, 0]} castShadow>
        <boxGeometry args={[w * 0.5, 0.08, d * 0.35]} />
        <meshStandardMaterial color="#a16207" />
      </mesh>
      <mesh position={[0, 0.275, 0]}>
        <boxGeometry args={[w * 0.45, 0.55, d * 0.3]} />
        <meshStandardMaterial color="#92400e" />
      </mesh>
      {/* Whiteboard */}
      <mesh position={[0, 1.5, -d / 2 + 0.06]}>
        <boxGeometry args={[w * 0.5, 1, 0.05]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
      {/* Chairs */}
      {Array.from({ length: 6 }).map((_, i) => {
        const isLeft = i % 2 === 0;
        const z = (Math.floor(i / 2) - 1) * 0.9;
        return (
          <group key={i} position={[isLeft ? -w * 0.32 : w * 0.32, 0.3, z]}>
            <mesh castShadow>
              <boxGeometry args={[0.4, 0.05, 0.4]} />
              <meshStandardMaterial color="#374151" />
            </mesh>
            <mesh position={[isLeft ? -0.18 : 0.18, 0.3, 0]}>
              <boxGeometry args={[0.05, 0.6, 0.4]} />
              <meshStandardMaterial color="#374151" />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}

export function Box3D({ size }: Box3DProps) {
  return (
    <Canvas shadows>
      <PerspectiveCamera makeDefault position={[8, 7, 9]} fov={40} />
      <OrbitControls
        enablePan={false}
        minDistance={6}
        maxDistance={20}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.2}
      />
      <ambientLight intensity={0.8} />
      <directionalLight position={[10, 12, 8]} intensity={1.2} castShadow />
      <directionalLight position={[-5, 8, -5]} intensity={0.4} />
      <Suspense fallback={null}>
        <Room size={size} />
      </Suspense>
    </Canvas>
  );
}
