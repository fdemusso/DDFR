import React from 'react';

/**
 * Componente per visualizzare un singolo riquadro volto
 * Memoizzato per evitare re-render inutili
 */
const FaceBox = ({ face, scaleX, scaleY, offsetX = 0, offsetY = 0, index }) => {
  const displayName = (face.fullName || face.name || "").toString().trim();
  const nameNormalized = displayName.toLowerCase();
  const isUnknown = !nameNormalized || nameNormalized.includes("sconosciuto") || nameNormalized === "unknown";
  
  const roleNormalized = (face.role || "").toString().trim().toLowerCase();
  
  let roleClass = "";
  if (isUnknown) {
    roleClass = "role-unknown";
  } else if (roleNormalized === "user") {
    roleClass = "role-user";
  } else if (roleNormalized === "guest") {
    roleClass = "role-guest";
  }

  // Calcola le coordinate finali considerando lo scaling e l'offset
  // Le coordinate dal backend sono relative al frame 640x480
  // Dobbiamo scalarle e applicare l'offset per compensare object-fit: cover
  const top = face.top * scaleY + offsetY;
  const left = face.left * scaleX + offsetX;
  const width = (face.right - face.left) * scaleX;
  const height = (face.bottom - face.top) * scaleY;
  
  // Debug logging (solo per il primo volto)
  if (index === 0) {
    console.log('FaceBox coordinate:', {
      original: { left: face.left, top: face.top, right: face.right, bottom: face.bottom },
      scaled: { left: left.toFixed(1), top: top.toFixed(1), width: width.toFixed(1), height: height.toFixed(1) },
      scaleX: scaleX.toFixed(3),
      scaleY: scaleY.toFixed(3),
      offsetX: offsetX.toFixed(1),
      offsetY: offsetY.toFixed(1)
    });
  }

  return (
    <div
      key={index}
      className={`face-box ${isUnknown ? 'unknown' : ''} ${roleClass}`}
      style={{
        top: `${top}px`,
        left: `${left}px`,
        width: `${width}px`,
        height: `${height}px`,
      }}
    >
      <div className="face-label">
        {displayName || "UNKNOWN"}
        {typeof face.age === "number" && face.age > 0 && (
          <span className="face-age">, {face.age}</span>
        )}
      </div>

      {/* Relationship come etichetta tipo apice in basso, tranne per ruolo user */}
      {!isUnknown && roleNormalized !== "user" && face.relationship && (
        <div className="face-relationship">
          {face.relationship}
        </div>
      )}
    </div>
  );
};

// Memoizza il componente per evitare re-render quando non necessario
export default React.memo(FaceBox, (prevProps, nextProps) => {
  // Confronta props rilevanti per decidere se re-renderizzare
  return (
    prevProps.face.id === nextProps.face.id &&
    prevProps.face.name === nextProps.face.name &&
    prevProps.face.top === nextProps.face.top &&
    prevProps.face.left === nextProps.face.left &&
    prevProps.face.right === nextProps.face.right &&
    prevProps.face.bottom === nextProps.face.bottom &&
    prevProps.scaleX === nextProps.scaleX &&
    prevProps.scaleY === nextProps.scaleY
  );
});






