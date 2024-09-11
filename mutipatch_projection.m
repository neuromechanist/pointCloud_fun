
forwardir = "~/git/pointcloud_fun/multi_patch/";
basedir = "~/expanse/projects/nemar/julie/Results/";
subjdir = 'OHSU_2020_11_13/';% subj 15, elecCoords_CS_32x32

% multi-path list
multi_pa = ["multi_patch_1_point_activation.mat", "multi_patch_2_point_activation.mat", "multi_patch_3_point_activation.mat", "multi_patch_4_point_activation.mat"];

%% load activation matrix and lead field matrix, project to scalp sensors
% do it five times, once with one patch, next with two patches, etc.
for i = 1:5
    pa = load([forwardir,multi_pa(i)]); % 485 x 787074
    lfm = load([forwardir,'jcFS_s1_LFM.mat']);% 208 x 80150

    %pamat = zeros(size(lfm.LFM,2),size(pa.point_activation,2)); % 80150 x 787074
    pamat = sparse(size(lfm.LFM,2),size(pa.point_activation,2)); % 80150 x 787074
    pamat(pa.LFM_indices,:) = pa.point_activation; % input sparse values

    eegact = lfm.LFM*pamat; % 208 scalp sensors x 787074
    clear pamat pa

    sname = ['GridForward475-11-13-',num2str(i)];%sname = 'GridForward-11-13';
    EEG = eeg_emptyset();
    EEG.data = eegact;
    EEG.pnts = size(EEG.data,2);
    EEG.nbchan = size(EEG.data ,1);
    EEG.srate = 1000;
    EEG.condition = 'ecog';
    EEG.filename = 'OHSU_2020_11_13_ForwardProjection';
    EEG.filepath = [forwardir,sname,'.set'];
    %EEG.setname = 'GridForward-11-13-DelNoiseICs'; % 248 chan grid
    EEG.setname = sname; %
    EEG=eeg_checkset(EEG);
    EEG=pop_chanedit(EEG, 'load',{[forwardir,'sensors.dat'],'filetype','sfp'},'eval','chans = pop_chancenter( chans, [],[]);');
    EEG = pop_select(EEG,'nochannel',1); % flatline
    EEG = pop_saveset( EEG,[sname,'.set'], [forwardir]);
end

%% Now, select only 128 channels and run AMICA on each of the five datasets
for i = 1:5
    dset = ['GridForward475-11-13-',num2str(i),'.set'];%dset = ['GridForward-11-13.set'];
    EEG = pop_loadset('filename',dset,'filepath',[forwardir]);%% HP, then rm channels, then avg ref
    % all good chans
    EEG.data = EEG.data*1e9;% used to make mean RMS = 86.5 for full 807 chan grid
    %EEG.data = EEG.data*5e8;% makes mean RMS = 38.4 for 807, which is close to rms of grid
    %EEG.data = EEG.data*1e3;% makes mean RMS = 22.8 for 248 chan grid, this time got 127 ICs
    mean(rms(EEG.data'))
    EEG = pop_saveset( EEG, 'filename',dset,'filepath',[forwardir]);
    % sub-sample channels and run ICA:
    numchans = 128;
    [subset idx pos] = loc_subsets(EEG.chanlocs, numchans, 0, 0);
    EEG = pop_select(EEG,'channel',subset{1});
    EEG = pop_saveset( EEG, 'filename',['GridForward128chan475-11-13-',num2str(i),'.set'],'filepath',[forwardir]);

    % Run AMICA:
    maxiter = 3000;  %'numprocs',4-16, 'ppernode',200, 'max_threads',1 (no hanging, but slower)
    num_models = 1;
    amicadir = [forwardir,'amicaScalp128Grid807-475bp-',num2str(i)];

    runamica17_nsg(EEG,'numprocs',4, 'max_threads',1, 'ppernode',25,'num_models',num_models,'batch',1,'outdir',amicadir,'lrate',0.002,'newtrate',0.5,'newt_start',num_models*50,'block_size',96,'pcakeep',size(EEG.data,1)-1,'do_reject',1,'max_iter',maxiter)
end
