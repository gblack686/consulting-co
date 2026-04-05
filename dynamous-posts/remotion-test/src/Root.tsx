import { Composition, Folder } from "remotion";
import { MyComposition, MyCompositionSchema } from "./MyComposition";
import { GBAutomationVideo, GB_VIDEO_DURATION } from "./GBAutomationVideo";

export const RemotionRoot = () => {
  return (
    <>
      <Folder name="Demo">
        <Composition
          id="MyComposition"
          component={MyComposition}
          durationInFrames={150}
          fps={30}
          width={1280}
          height={720}
          schema={MyCompositionSchema}
          defaultProps={{
            titleText: "Remotion",
            subtitleText: "Video as Code",
            badgeText: "Live Preview",
            accentColor: "#e94560",
          }}
        />
      </Folder>

      <Folder name="GB-Automation">
        <Composition
          id="GBAutomationVideo"
          component={GBAutomationVideo}
          durationInFrames={GB_VIDEO_DURATION}
          fps={30}
          width={1280}
          height={720}
        />
      </Folder>
    </>
  );
};
